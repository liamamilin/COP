"""Create -> invoke -> inspect ONE tool-calling agent in ONE process.

Tool: get_product_info (local product catalog lookup).
Message chain: human -> assistant(tool_calls) -> tool -> ai.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from config import ConfigError, Settings, load_settings
from evidence import compute_evidence_hash
from tool import get_product_info


def _wrap_tool():
    from langchain_core.tools import StructuredTool

    return StructuredTool.from_function(
        func=get_product_info,
        name="get_product_info",
        description=(
            "查询产品目录中指定 ID 的产品信息。返回产品名称、价格、分类和库存状态。"
            "product_id 必须是 P001 到 P005 之间的字符串。"
            "如果产品不存在，返回错误信息。"
        ),
    )


TOOL = _wrap_tool()


class _ToolCallMockModel:
    """Offline mock that simulates a tool-calling sequence.

    First call: returns AIMessage with tool_calls (agent executes the tool).
    Second call: returns AIMessage with final answer incorporating tool result.
    """

    def __init__(self, tool_result: dict, final_answer: str):
        from langchain_core.messages import AIMessage, ToolMessage

        self._tool_result = tool_result
        self._final_answer = final_answer
        self._call_count = 0

    def bind_tools(self, tools, **kwargs):
        return self

    @property
    def responses(self):
        return []

    def invoke(self, messages, **kwargs):
        from langchain_core.messages import AIMessage

        self._call_count += 1

        if self._call_count == 1:
            last_msg = messages[-1]
            return AIMessage(
                content="",
                tool_calls=[{
                    "name": "get_product_info",
                    "args": {"product_id": "P001"},
                    "id": "call_offline_mock_001",
                }],
            )

        return AIMessage(content=self._final_answer)

    def __call__(self, messages, **kwargs):
        return self.invoke(messages, **kwargs)


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
    model_with_tools = model.bind_tools([TOOL])
    return create_agent(
        model=model_with_tools,
        tools=[TOOL],
        system_prompt=settings.system_prompt,
    )


def build_offline_agent() -> Any:
    from langchain.agents import create_agent

    mock = _ToolCallMockModel(
        tool_result={"name": "LangChain 入门教程", "price": 99.00, "category": "教程", "in_stock": True},
        final_answer="LangChain 入门教程的价格是 99.00 元。",
    )
    return create_agent(
        model=mock,
        tools=[TOOL],
        system_prompt="Offline tool-calling plumbing check only.",
    )


def invoke_agent(agent: Any, message: str) -> dict[str, Any]:
    from langsmith import tracing_context

    with tracing_context(enabled=False):
        return agent.invoke({"messages": [{"role": "user", "content": message}]})


def inspect_response(result: dict[str, Any], message: str) -> dict[str, Any]:
    """Validate the tool-calling message chain.

    Expected: human -> ai(tool_calls) -> tool -> ai(final answer).
    """
    messages = result.get("messages", [])
    types = [m.type for m in messages]

    if len(types) < 4:
        raise ValueError(
            f"Tool-calling chain needs >= 4 messages (human/ai-tool/tool/ai), got {len(types)}: {types}"
        )
    if types[0] != "human":
        raise ValueError(f"First message must be human, got {types[0]}")
    if messages[0].content != message:
        raise ValueError("The returned input is not the message this run sent.")

    ai_with_calls = None
    tool_msg = None
    for m in messages[1:]:
        if m.type == "ai" and hasattr(m, "tool_calls") and m.tool_calls:
            ai_with_calls = m
        elif m.type == "tool":
            tool_msg = m

    if ai_with_calls is None:
        raise ValueError("No assistant message with tool_calls found in the chain.")
    if tool_msg is None:
        raise ValueError("No tool result message found in the chain.")

    tool_call = ai_with_calls.tool_calls[0]
    if tool_call["name"] != "get_product_info":
        raise ValueError(f"Tool name must be get_product_info, got {tool_call['name']}")
    if "product_id" not in tool_call["args"]:
        raise ValueError("tool_calls args must include product_id")

    final_ai = messages[-1]
    if final_ai.type != "ai":
        raise ValueError(f"Last message must be ai, got {final_ai.type}")
    if not isinstance(final_ai.content, str) or not final_ai.content.strip():
        raise ValueError("Final AI message must contain nonempty text.")

    tool_result = json.loads(tool_msg.content)

    return {
        "input": message,
        "messages": [
            {
                "type": m.type,
                "content": m.content,
                **({"tool_calls": m.tool_calls} if hasattr(m, "tool_calls") and m.tool_calls else {}),
                **({"tool_call_id": m.tool_call_id} if hasattr(m, "tool_call_id") else {}),
            }
            for m in messages
        ],
        "tool_name": tool_call["name"],
        "tool_args": tool_call["args"],
        "tool_call_id": tool_call["id"],
        "tool_result": tool_result,
        "answer": final_ai.content,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--message",
        default="P001 的价格是多少？",
        help="User question to send to the agent.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true", help="Mock tool sequence; no provider or key.")
    mode.add_argument("--create-only", action="store_true", help="Construct agent only; no API request.")
    parser.add_argument("--output", type=Path, help="Save this run to a NEW JSON file.")
    args = parser.parse_args(argv)
    if not args.message.strip():
        parser.error("--message must be nonempty")
    if args.output is not None and args.output.exists():
        parser.error("--output already exists; choose a new filename. Nothing has been invoked.")
    try:
        settings = None if args.offline else load_settings()
        if args.offline:
            agent = build_offline_agent()
        else:
            agent = build_agent(settings)
        if args.create_only:
            report: dict[str, Any] = {
                "mode": "construction-only",
                "status": "created",
                "configuration": settings.public_summary() if settings else None,
                "tool": "get_product_info",
                "note": "No provider request. Agent constructed with tool binding.",
            }
        else:
            result = invoke_agent(agent, args.message)
            inspected = inspect_response(result, args.message)
            report = {
                "mode": "offline-mock" if args.offline else "provider-response",
                "configuration": settings.public_summary() if settings else None,
                **inspected,
                "evidence_hash": compute_evidence_hash(inspected),
                "note": (
                    "Mock tool sequence: not evidence of real LLM tool-calling quality."
                    if args.offline
                    else "One tool-calling invocation; verify tool result matches final answer."
                ),
            }
        encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output is not None:
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(encoded)
        print(encoded, end="")
        return 0
    except ConfigError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2
    except Exception as error:
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
