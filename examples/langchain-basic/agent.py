"""Create -> invoke -> inspect ONE agent in ONE process; no tools or memory yet."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from config import ConfigError, Settings, load_settings


def build_agent(settings: Settings) -> Any:
    from langchain.agents import create_agent
    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
        timeout=30,
        max_retries=0,
        use_responses_api=False,
    )
    return create_agent(model=model, tools=[], system_prompt=settings.system_prompt)


def build_offline_agent() -> Any:
    from langchain.agents import create_agent
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
    from langchain_core.messages import AIMessage

    model = FakeMessagesListChatModel(
        responses=[AIMessage(content="This is a scripted offline reply, not an LLM response.")]
    )
    return create_agent(model=model, tools=[], system_prompt="Offline plumbing check only.")


def build_agent_from_identifier(settings: Settings) -> Any:
    """Optional model initializer; same explicit config, agent and downstream flow."""
    from langchain.agents import create_agent
    from langchain.chat_models import init_chat_model

    model = init_chat_model(
        model=settings.model,
        model_provider="openai",
        api_key=settings.api_key,
        base_url=settings.base_url,
        timeout=30,
        max_retries=0,
        use_responses_api=False,
    )
    return create_agent(model=model, tools=[], system_prompt=settings.system_prompt)


def invoke_agent(agent: Any, message: str) -> dict[str, Any]:
    from langsmith import tracing_context

    # This lesson does not configure a telemetry service, even if the parent
    # terminal happens to enable LangSmith. Offline must stay genuinely offline.
    with tracing_context(enabled=False):
        return agent.invoke({"messages": [{"role": "user", "content": message}]})


def inspect_response(result: dict[str, Any], message: str) -> dict[str, Any]:
    messages = result.get("messages", [])
    types = [item.type for item in messages]
    if types != ["human", "ai"]:
        raise ValueError("The completed, text-only, no-tool Basic profile needs human -> ai.")
    if messages[0].content != message:
        raise ValueError("The returned input is not the message this run sent.")
    answer = messages[-1].content
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("The final AI message must contain nonempty text in this Basic profile.")
    return {
        "input": message,
        "messages": [{"type": item.type, "content": item.content} for item in messages],
        "answer": answer,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", default="Name one benefit of using an agent harness.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true", help="Fixed reply; no provider or key.")
    mode.add_argument("--create-only", action="store_true", help="Construct only; no API request.")
    parser.add_argument("--model-init", choices=["direct", "identifier"], default="direct")
    parser.add_argument("--output", type=Path, help="Save this run to a NEW JSON file.")
    args = parser.parse_args(argv)
    if not args.message.strip():
        parser.error("--message must be nonempty")
    if args.offline and args.model_init != "direct":
        parser.error("--offline uses a fixed local model, not a provider initializer")
    if args.output is not None and args.output.exists():
        parser.error("--output already exists; choose a new filename. Nothing has been invoked.")
    try:
        settings = None if args.offline else load_settings()
        if settings is None:
            agent = build_offline_agent()
        else:
            factory = build_agent if args.model_init == "direct" else build_agent_from_identifier
            agent = factory(settings)
        if args.create_only:
            report: dict[str, Any] = {
                "mode": "construction-only",
                "status": "created",
                "configuration": settings.public_summary(),
                "note": "No provider request. This object ends when this process exits.",
            }
        else:
            result = invoke_agent(agent, args.message)
            report = {
                "mode": "offline-fixture" if args.offline else "provider-response",
                "configuration": None if settings is None else settings.public_summary(),
                **inspect_response(result, args.message),
                "note": (
                    "Fixed local reply: not evidence of real LLM quality or provider compatibility."
                    if args.offline
                    else "One no-tool invocation; this is not a tool-use or memory verification."
                ),
            }
        encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output is not None:
            # Exclusive create: a race must not overwrite an existing learner artifact.
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(encoded)
        print(encoded, end="")
        return 0
    except ConfigError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2
    except Exception as error:
        # Provider exception strings can include request details. Do not dump
        # them or credentials into the learner's terminal/JSON report.
        status = getattr(error, "status_code", None)
        suffix = f" (HTTP {status})" if isinstance(status, int) else ""
        print(
            f"Run failed: {type(error).__name__}{suffix}. Check the lesson's failure table; "
            "no successful run report was written.",
            file=sys.stderr,
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
