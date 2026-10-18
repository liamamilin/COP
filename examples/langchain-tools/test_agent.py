"""Offline tests for the tool-calling agent.

Verifies: message chain shape, tool call extraction, inspect validation,
output saving, negative cases. No provider or API key needed.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from agent import (
    TOOL,
    build_offline_agent,
    inspect_response,
    invoke_agent,
)


class TestToolWrapping:
    def test_tool_name(self):
        assert TOOL.name == "get_product_info"

    def test_tool_has_description(self):
        assert TOOL.description
        assert "product_id" in TOOL.description.lower() or "产品" in TOOL.description

    def test_tool_is_callable(self):
        result = TOOL.invoke({"product_id": "P001"})
        assert result["name"] == "LangChain 入门教程"


class TestOfflineAgentCreation:
    def test_build_offline_agent_succeeds(self):
        agent = build_offline_agent()
        assert agent is not None

    def test_offline_invoke_produces_tool_chain(self):
        agent = build_offline_agent()
        result = invoke_agent(agent, "P001 的价格是多少？")
        messages = result["messages"]
        types = [m.type for m in messages]
        assert types[0] == "human"
        assert "ai" in types
        assert "tool" in types


class TestInspectResponse:
    def _get_offline_result(self, message="P001 的价格是多少？"):
        agent = build_offline_agent()
        return invoke_agent(agent, message)

    def test_inspect_extracts_tool_name(self):
        result = self._get_offline_result()
        inspected = inspect_response(result, "P001 的价格是多少？")
        assert inspected["tool_name"] == "get_product_info"

    def test_inspect_extracts_tool_args(self):
        result = self._get_offline_result()
        inspected = inspect_response(result, "P001 的价格是多少？")
        assert inspected["tool_args"]["product_id"] == "P001"

    def test_inspect_extracts_tool_result(self):
        result = self._get_offline_result()
        inspected = inspect_response(result, "P001 的价格是多少？")
        assert inspected["tool_result"]["name"] == "LangChain 入门教程"
        assert inspected["tool_result"]["price"] == 99.0

    def test_inspect_extracts_answer(self):
        result = self._get_offline_result()
        inspected = inspect_response(result, "P001 的价格是多少？")
        assert "99" in inspected["answer"]
        assert "LangChain" in inspected["answer"]

    def test_inspect_has_tool_call_id(self):
        result = self._get_offline_result()
        inspected = inspect_response(result, "P001 的价格是多少？")
        assert inspected["tool_call_id"]
        assert inspected["tool_call_id"].startswith("call_")

    def test_inspect_message_chain_has_four_types(self):
        result = self._get_offline_result()
        inspected = inspect_response(result, "P001 的价格是多少？")
        types = [m["type"] for m in inspected["messages"]]
        assert types == ["human", "ai", "tool", "ai"]

    def test_inspect_rejects_wrong_input(self):
        result = self._get_offline_result()
        with pytest.raises(ValueError, match="not the message this run sent"):
            inspect_response(result, "different message")


class TestInspectNegativeCases:
    def test_rejects_too_few_messages(self):
        from langchain_core.messages import AIMessage, HumanMessage

        fake_result = {
            "messages": [
                HumanMessage(content="hello"),
                AIMessage(content="hi"),
            ]
        }
        with pytest.raises(ValueError, match="needs >= 4 messages"):
            inspect_response(fake_result, "hello")

    def test_rejects_no_tool_calls(self):
        from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

        fake_result = {
            "messages": [
                HumanMessage(content="hello"),
                AIMessage(content="I don't use tools"),
                ToolMessage(content="{}", tool_call_id="x"),
                AIMessage(content="answer"),
            ]
        }
        with pytest.raises(ValueError, match="No assistant message with tool_calls"):
            inspect_response(fake_result, "hello")

    def test_rejects_wrong_tool_name(self):
        from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

        fake_result = {
            "messages": [
                HumanMessage(content="hello"),
                AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "wrong_tool",
                        "args": {"product_id": "P001"},
                        "id": "call_001",
                    }],
                ),
                ToolMessage(content="{}", tool_call_id="call_001"),
                AIMessage(content="answer"),
            ]
        }
        with pytest.raises(ValueError, match="Tool name must be get_product_info"):
            inspect_response(fake_result, "hello")


class TestMainCLI:
    def test_offline_mode_returns_zero(self):
        from agent import main

        exit_code = main(["--offline"])
        assert exit_code == 0

    def test_offline_with_custom_message(self):
        from agent import main

        exit_code = main(["--offline", "--message", "P003 还有货吗？"])
        assert exit_code == 0

    def test_output_creates_file(self, tmp_path):
        from agent import main

        output = tmp_path / "run.json"
        exit_code = main(["--offline", "--output", str(output)])
        assert exit_code == 0
        assert output.exists()
        data = json.loads(output.read_text())
        assert data["mode"] == "offline-mock"
        assert data["tool_name"] == "get_product_info"

    def test_output_refuses_overwrite(self, tmp_path):
        from agent import main

        output = tmp_path / "run.json"
        output.write_text("{}")
        with pytest.raises(SystemExit) as exc_info:
            main(["--offline", "--output", str(output)])
        assert exc_info.value.code != 0

    def test_no_config_returns_2(self, monkeypatch):
        import agent
        from config import ConfigError

        def fake_load_settings(*args, **kwargs):
            raise ConfigError("No configuration available")

        monkeypatch.setattr(agent, "load_settings", fake_load_settings)
        exit_code = agent.main([])
        assert exit_code == 2
