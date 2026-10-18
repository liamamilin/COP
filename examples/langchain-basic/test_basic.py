"""Offline acceptance and negative cases. No provider, secrets or database needed."""

import contextlib
import copy
import io
import json
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import ClassVar
from unittest.mock import patch

import agent
import httpx
from config import ConfigError, Settings, load_settings
from inspect_result import validate_report
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

HERE = Path(__file__).resolve().parent
SAFE_ENV = {
    "LC_API_KEY": "offline-dummy-not-a-real-key",
    "LC_BASE_URL": "https://provider.example/v1",
    "LC_MODEL": "test-model",
    "LC_SYSTEM_PROMPT": "Answer briefly.",
}


class BasicAcceptance(unittest.TestCase):
    def setUp(self):
        self.guard = contextlib.ExitStack()
        self.addCleanup(self.guard.close)
        self.guard.enter_context(
            patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden"))
        )
        self.guard.enter_context(
            patch.object(httpx.Client, "send", side_effect=AssertionError("HTTP forbidden"))
        )
        self.guard.enter_context(
            patch.object(httpx.AsyncClient, "send", side_effect=AssertionError("HTTP forbidden"))
        )
        self.guard.enter_context(
            patch.dict(
                os.environ,
                {
                    "LANGSMITH_TRACING": "true",
                    "LANGSMITH_API_KEY": "offline-dummy",
                    "OPENAI_API_KEY": "wrong-parent-key",
                    "OPENAI_BASE_URL": "https://wrong-parent.example/v1",
                    "OPENAI_API_BASE": "https://also-wrong.example/v1",
                },
            )
        )
        self.folder = Path(
            self.guard.enter_context(tempfile.TemporaryDirectory(prefix="cop-basic-test-"))
        )
        self.env_file = self.folder / ".env"

    def test_dotenv_is_named_nonmutating_and_process_wins(self):
        self.env_file.write_text(
            "\n".join(f"{key}={value}" for key, value in SAFE_ENV.items()), encoding="utf-8"
        )
        before = dict(os.environ)
        settings = load_settings(self.env_file, {"LC_MODEL": "overridden"})
        self.assertEqual(settings.model, "overridden")
        self.assertEqual(settings.base_url, SAFE_ENV["LC_BASE_URL"])
        self.assertEqual(before, dict(os.environ))
        self.assertNotIn(settings.api_key, repr(settings))
        self.assertNotIn(settings.api_key, json.dumps(settings.public_summary()))
        with self.assertRaisesRegex(ConfigError, "LC_MODEL"):
            load_settings(self.env_file, {"LC_MODEL": ""})

    def test_no_parent_dotenv_or_sdk_fallback(self):
        self.env_file.write_text(
            "\n".join(f"{key}={value}" for key, value in SAFE_ENV.items()), encoding="utf-8"
        )
        child_file = self.folder / "lesson" / ".env"
        with self.assertRaisesRegex(ConfigError, "LC_API_KEY"):
            load_settings(child_file, {"OPENAI_API_KEY": "wrong-parent-key"})

    def test_placeholders_empty_and_interpolation_are_rejected(self):
        for value in ("", "replace-with-key", "${OPENAI_API_KEY}"):
            with self.subTest(value=value), self.assertRaisesRegex(ConfigError, "LC_API_KEY"):
                load_settings(self.env_file, {**SAFE_ENV, "LC_API_KEY": value})

    def test_endpoint_rejects_hidden_credentials_and_request_url(self):
        for endpoint in (
            "http://remote.example/v1",
            "file:///tmp",
            "https://user:password@host/v1",
            "https://host/v1?api_key=secret",
            "https://host/v1#fragment",
            "https://host/v1/chat/completions",
            "https://host/v1/responses",
            "https://host:bad/v1",
        ):
            with self.subTest(endpoint=endpoint), self.assertRaises(ConfigError) as failure:
                load_settings(self.env_file, {**SAFE_ENV, "LC_BASE_URL": endpoint})
            self.assertNotIn("secret", str(failure.exception))
            self.assertNotIn("password", str(failure.exception))
        local = load_settings(
            self.env_file, {**SAFE_ENV, "LC_BASE_URL": "http://127.0.0.1:8000/v1/"}
        )
        self.assertEqual(local.base_url, "http://127.0.0.1:8000/v1")

    def test_both_model_initializers_preserve_explicit_configuration_and_prompt(self):
        settings = load_settings(self.env_file, SAFE_ENV)
        for factory in (agent.build_agent, agent.build_agent_from_identifier):
            with self.subTest(factory=factory.__name__):
                # Capture the actual ChatOpenAI object at the graph boundary.
                with patch("langchain.agents.create_agent") as create:
                    factory(settings)
                kwargs = create.call_args.kwargs
                model = kwargs["model"]
                self.assertEqual(model.model_name, settings.model)
                self.assertEqual(model.openai_api_key.get_secret_value(), settings.api_key)
                self.assertEqual(str(model.root_client.base_url).rstrip("/"), settings.base_url)
                self.assertEqual(model.max_retries, 0)
                self.assertEqual(kwargs["system_prompt"], settings.system_prompt)
                self.assertEqual(kwargs["tools"], [])
                # Construct the real graph too, without invoking a provider.
                graph = factory(settings)
                self.assertTrue(callable(graph.invoke))

    def test_real_graph_offline_run_and_saved_report(self):
        output = self.folder / "run.json"
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            code = agent.main(["--offline", "--message", "My input", "--output", str(output)])
        self.assertEqual(code, 0)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report, json.loads(stdout.getvalue()))
        self.assertEqual(validate_report(report), "offline-fixture")
        self.assertEqual(report["input"], "My input")
        self.assertEqual([message["type"] for message in report["messages"]], ["human", "ai"])
        self.assertIn("not an LLM response", report["answer"])
        self.assertIsNone(report["configuration"])

    def test_system_prompt_and_user_input_reach_the_actual_model_node(self):
        from langchain.agents import create_agent
        from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

        class RecordingModel(FakeMessagesListChatModel):
            seen: ClassVar[list] = []

            def _generate(self, messages, stop=None, run_manager=None, **kwargs):
                type(self).seen.append(messages)
                return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

        graph = create_agent(
            model=RecordingModel(responses=[AIMessage(content="Fixed answer")]),
            tools=[],
            system_prompt="This instruction must survive graph assembly.",
        )
        result = agent.invoke_agent(graph, "This is the actual user input.")
        observed = RecordingModel.seen[0]
        self.assertEqual([item.type for item in observed], ["system", "human"])
        self.assertEqual(observed[0].content, "This instruction must survive graph assembly.")
        self.assertEqual(observed[1].content, "This is the actual user input.")
        self.assertEqual(
            agent.inspect_response(result, observed[1].content)["answer"], "Fixed answer"
        )

    def test_independent_inspector_rejects_false_passes(self):
        report = {
            "mode": "offline-fixture",
            "input": "Hi",
            "answer": "Hello",
            "messages": [{"type": "human", "content": "Hi"}, {"type": "ai", "content": "Hello"}],
        }
        validate_report(report)
        mutations = (
            {"mode": "construction-only"},
            {"input": "Other"},
            {"answer": "Made up"},
            {"messages": [{"type": "ai", "content": "Hello"}]},
            {"messages": [{"type": "human", "content": "Hi"}, {"type": "ai", "content": ""}]},
            {"messages": [None, None]},
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_report({**copy.deepcopy(report), **mutation})

    def test_runtime_inspection_rejects_missing_wrong_or_empty_output(self):
        for messages in (
            [],
            [AIMessage(content="Answer")],
            [HumanMessage(content="Wrong"), AIMessage(content="A")],
            [HumanMessage(content="Hi"), AIMessage(content="")],
            [SystemMessage(content="Hi"), AIMessage(content="A")],
        ):
            with self.subTest(messages=messages), self.assertRaises(ValueError):
                agent.inspect_response({"messages": messages}, "Hi")

    def test_existing_output_stops_before_invocation(self):
        output = self.folder / "keep.json"
        output.write_text("keep", encoding="utf-8")
        with (
            patch.object(agent, "build_offline_agent") as build,
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit) as failure,
        ):
            agent.main(["--offline", "--output", str(output)])
        self.assertEqual(failure.exception.code, 2)
        build.assert_not_called()
        self.assertEqual(output.read_text(encoding="utf-8"), "keep")

    def test_provider_exception_is_redacted_and_not_saved_as_success(self):
        output = self.folder / "failed.json"
        with (
            patch.object(
                agent,
                "load_settings",
                return_value=Settings(
                    api_key="secret-not-to-log",
                    base_url=SAFE_ENV["LC_BASE_URL"],
                    model="test-model",
                    system_prompt="Brief",
                ),
            ),
            patch.object(agent, "build_agent", side_effect=RuntimeError("secret-not-to-log")),
            contextlib.redirect_stderr(io.StringIO()) as stderr,
        ):
            self.assertEqual(agent.main(["--output", str(output)]), 3)
        self.assertNotIn("secret-not-to-log", stderr.getvalue())
        self.assertIn("RuntimeError", stderr.getvalue())
        self.assertFalse(output.exists())

    def test_offline_cli_from_another_directory_and_inspection_without_keys(self):
        output = self.folder / "subprocess.json"
        # No inherited credentials or telemetry. Parent-process guards cannot
        # intercept a subprocess, so network interception is tested above.
        environment = {"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"}
        run = subprocess.run(
            [sys.executable, str(HERE / "agent.py"), "--offline", "--output", str(output)],
            cwd=self.folder,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        inspect = subprocess.run(
            [sys.executable, str(HERE / "inspect_result.py"), str(output)],
            cwd=self.folder,
            env=environment,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(inspect.returncode, 0, inspect.stderr)
        self.assertIn("NOT VERIFIED", inspect.stdout)
        self.assertIn("not a semantic answer grade", inspect.stdout)

    def test_copyable_cop_bootstrap_from_a_fresh_lesson_directory(self):
        fixture_path = HERE.parents[1] / "fixtures/langchain-basic-cop.json"
        curriculum = json.loads(fixture_path.read_text(encoding="utf-8"))
        filenames = {
            "config.py",
            "agent.py",
            "inspect_result.py",
            ".env.example",
            "requirements.txt",
        }
        for stage in curriculum["stages"]:
            for detail in stage["implementation_details"]:
                filename = detail["title"].removeprefix("保存 ")
                if filename in filenames:
                    (self.folder / filename).write_text(detail["command"], encoding="utf-8")
        self.assertTrue(all((self.folder / name).is_file() for name in filenames))
        # These values are deliberately inert; construction is not an API call.
        (self.folder / ".env").write_text(
            "\n".join(f"{key}={value}" for key, value in SAFE_ENV.items()), encoding="utf-8"
        )
        environment = {"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"}
        commands = (
            ["config.py"],
            ["agent.py", "--create-only"],
            ["agent.py", "--model-init", "identifier", "--create-only"],
            ["agent.py", "--offline", "--message", "Copied COP input", "--output", "cop-run.json"],
            ["inspect_result.py", "cop-run.json"],
        )
        for arguments in commands:
            result = subprocess.run(
                [sys.executable, *arguments],
                cwd=self.folder,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn(SAFE_ENV["LC_API_KEY"], result.stdout + result.stderr)
        report = json.loads((self.folder / "cop-run.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_report(report), "offline-fixture")
        self.assertEqual(report["input"], "Copied COP input")


if __name__ == "__main__":
    unittest.main(verbosity=2)
