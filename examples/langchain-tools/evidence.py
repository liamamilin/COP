"""Independent verification of a tool-calling run's evidence chain.

T04 deliverable: proves the tool was actually executed (not just claimed by the model),
the tool_call_id links the AI tool_calls to the Tool message, and the evidence chain
is content-bound for reproducibility.
"""

import hashlib
import json
from typing import Any


def re_execute_tool(tool_name: str, tool_args: dict) -> Any:
    """Re-execute the tool with the given args to verify the recorded result is genuine.

    Only supports known tools. Raises ValueError for unknown tools.
    """
    if tool_name == "get_product_info":
        from tool import get_product_info

        return get_product_info(**tool_args)
    raise ValueError(f"Unknown tool for re-execution: {tool_name}")


def extract_tool_call_chain(messages: list[dict]) -> list[dict]:
    """Extract ordered (tool_call, tool_result) pairs from a message list.

    Each pair links by tool_call_id: the AI message's tool_calls[].id must match
    the Tool message's tool_call_id.
    """
    tool_calls_by_id: dict[str, dict] = {}
    tool_results_by_id: dict[str, dict] = {}

    for msg in messages:
        msg_type = msg.get("type", "")
        if msg_type == "ai" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                tc_id = tc.get("id")
                if tc_id:
                    tool_calls_by_id[tc_id] = tc
        elif msg_type == "tool":
            tc_id = msg.get("tool_call_id")
            if tc_id:
                tool_results_by_id[tc_id] = msg

    pairs = []
    for tc_id in tool_calls_by_id:
        if tc_id not in tool_results_by_id:
            raise ValueError(
                f"tool_call_id {tc_id} has an AI tool_call but no matching Tool message."
            )
        pairs.append({
            "tool_call_id": tc_id,
            "tool_call": tool_calls_by_id[tc_id],
            "tool_result_message": tool_results_by_id[tc_id],
        })

    if not pairs:
        raise ValueError("No tool_call / tool_result pairs found in the message chain.")

    return pairs


def verify_single_call_evidence(run_data: dict) -> dict:
    """Verify a single-tool-call run's evidence chain.

    Checks:
    1. tool_call_id linkage: AI tool_calls[].id == Tool tool_call_id.
    2. Tool result matches re-execution of the tool with recorded args.
    3. Tool name in the call matches the expected tool.
    4. Final answer is present and non-empty.

    Returns a verification report dict.
    """
    messages = run_data.get("messages", [])
    if len(messages) < 4:
        return {"verified": False, "reason": f"Chain too short: {len(messages)} messages"}

    pairs = extract_tool_call_chain(messages)
    if len(pairs) != 1:
        return {
            "verified": False,
            "reason": f"Expected 1 tool_call pair for single-call verification, got {len(pairs)}",
        }

    pair = pairs[0]
    tool_call = pair["tool_call"]
    tool_name = tool_call.get("name", "")
    tool_args = tool_call.get("args", {})
    tool_call_id = pair["tool_call_id"]

    tool_result_msg = pair["tool_result_message"]
    recorded_result = json.loads(tool_result_msg["content"])

    try:
        actual_result = re_execute_tool(tool_name, tool_args)
    except Exception as error:
        return {"verified": False, "reason": f"Re-execution failed: {error}"}

    if actual_result != recorded_result:
        return {
            "verified": False,
            "reason": (
                f"Tool result mismatch: recorded={recorded_result}, "
                f"re-executed={actual_result}"
            ),
        }

    final_ai = messages[-1]
    if final_ai.get("type") != "ai":
        return {"verified": False, "reason": f"Last message not ai: {final_ai.get('type')}"}
    if not isinstance(final_ai.get("content"), str) or not final_ai["content"].strip():
        return {"verified": False, "reason": "Final AI message is empty"}

    return {
        "verified": True,
        "tool_name": tool_name,
        "tool_args": tool_args,
        "tool_call_id": tool_call_id,
        "tool_result": recorded_result,
        "re_execution_match": True,
        "answer": final_ai["content"],
    }


def verify_multi_call_evidence(run_data: dict) -> dict:
    """Verify a multi-tool-call run's evidence chain.

    Same checks as single-call, but handles multiple (tool_call, tool_result) pairs.
    """
    messages = run_data.get("messages", [])
    if len(messages) < 4:
        return {"verified": False, "reason": f"Chain too short: {len(messages)} messages"}

    pairs = extract_tool_call_chain(messages)

    results = []
    all_verified = True
    for pair in pairs:
        tool_call = pair["tool_call"]
        tool_name = tool_call.get("name", "")
        tool_args = tool_call.get("args", {})
        tool_call_id = pair["tool_call_id"]
        tool_result_msg = pair["tool_result_message"]
        recorded_result = json.loads(tool_result_msg["content"])

        try:
            actual_result = re_execute_tool(tool_name, tool_args)
        except Exception as error:
            results.append({
                "tool_call_id": tool_call_id,
                "tool_name": tool_name,
                "verified": False,
                "reason": f"Re-execution failed: {error}",
            })
            all_verified = False
            continue

        match = actual_result == recorded_result
        if not match:
            all_verified = False
        results.append({
            "tool_call_id": tool_call_id,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "verified": match,
            "recorded_result": recorded_result,
            "re_executed_result": actual_result if not match else None,
        })

    final_ai = messages[-1]
    answer_ok = (
        final_ai.get("type") == "ai"
        and isinstance(final_ai.get("content"), str)
        and bool(final_ai["content"].strip())
    )

    return {
        "verified": all_verified and answer_ok,
        "pair_count": len(pairs),
        "pairs": results,
        "answer_present": answer_ok,
    }


def compute_evidence_hash(run_data: dict) -> str:
    """SHA-256 of the evidence-relevant fields for content binding.

    Hashes: input, messages (types + contents + tool_calls + tool_call_ids),
    tool_name, tool_args, tool_result, answer. Excludes mode, configuration, note.
    """
    evidence = {
        "input": run_data.get("input"),
        "messages": run_data.get("messages"),
        "tool_name": run_data.get("tool_name"),
        "tool_args": run_data.get("tool_args"),
        "tool_call_id": run_data.get("tool_call_id"),
        "tool_result": run_data.get("tool_result"),
        "answer": run_data.get("answer"),
    }
    canonical = json.dumps(evidence, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
