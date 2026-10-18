"""Read-only verifier for a saved tool-calling run.

Does not read keys, create agents, or call APIs. Checks:
- message chain shape (human -> ai(tool_calls) -> tool -> ai)
- tool_call_id linkage
- tool result matches re-execution
- evidence_hash integrity
"""

import json
import sys
from pathlib import Path

from evidence import (
    compute_evidence_hash,
    extract_tool_call_chain,
    verify_multi_call_evidence,
    verify_single_call_evidence,
)


def verify_file(path: Path) -> int:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}")
        return 1

    mode = data.get("mode", "<missing>")
    print(f"mode: {mode}")

    messages = data.get("messages", [])
    types = [m.get("type", "?") for m in messages]
    print(f"message types: {' -> '.join(types)}")
    print(f"message count: {len(types)}")

    if mode == "construction-only":
        print("\nSKIP: construction-only run has no invocation to verify.")
        return 0

    input_text = data.get("input", "")
    answer = data.get("answer", "")
    print(f"input: {input_text}")
    print(f"answer: {answer}")

    tool_name = data.get("tool_name", "<missing>")
    tool_args = data.get("tool_args", {})
    tool_call_id = data.get("tool_call_id", "<missing>")
    print(f"\ntool_name: {tool_name}")
    print(f"tool_args: {json.dumps(tool_args, ensure_ascii=False)}")
    print(f"tool_call_id: {tool_call_id}")

    tool_result = data.get("tool_result")
    print(f"tool_result: {json.dumps(tool_result, ensure_ascii=False)}")

    print("\n--- Evidence verification ---")

    try:
        pairs = extract_tool_call_chain(data.get("messages", []))
    except ValueError as error:
        print(f"VERIFICATION FAILED: {error}")
        return 1

    if len(pairs) == 1:
        report = verify_single_call_evidence(data)
        if report["verified"]:
            print("tool_call_id linkage: OK")
            print("re-execution match: OK")
            print("final answer present: OK")
        else:
            print(f"VERIFICATION FAILED: {report.get('reason', 'unknown')}")
            return 1
    else:
        print(f"Detected {len(pairs)} tool_call pairs — using multi-call verifier.")
        report = verify_multi_call_evidence(data)
        if not report["verified"]:
            print("VERIFICATION FAILED:")
            for p in report.get("pairs", []):
                status = "OK" if p["verified"] else f"FAILED ({p.get('reason', 'mismatch')})"
                print(f"  {p['tool_call_id']}: {p['tool_name']}({json.dumps(p['tool_args'], ensure_ascii=False)}) -> {status}")
            if not report.get("answer_present"):
                print("  Final answer: MISSING")
            return 1
        print(f"All {report['pair_count']} tool_call pairs verified (re-execution match).")
        print("Final answer present: OK")

    recorded_hash = data.get("evidence_hash")
    if recorded_hash:
        actual_hash = compute_evidence_hash(data)
        if actual_hash == recorded_hash:
            print(f"evidence_hash: MATCH ({actual_hash[:16]}...)")
        else:
            print(f"evidence_hash: MISMATCH (recorded={recorded_hash[:16]}..., computed={actual_hash[:16]}...)")
            return 1
    else:
        print("evidence_hash: NOT PRESENT (multi-call or predates T04)")

    print("\n--- Summary ---")
    if mode == "offline-mock":
        print("PASS: tool-calling chain structure and evidence integrity verified.")
        print("NOTE: offline mock — tool result is from _ToolCallMockModel, not a real LLM.")
        print("LIVE PROVIDER AND LEARNER ACCEPTANCE: NOT VERIFIED")
    elif mode == "provider-response":
        print("PASS: tool-calling chain, re-execution match, and evidence hash verified.")
        print("Semantic judgment (does the answer correctly use tool facts?) requires human review.")
    else:
        print(f"PASS with unknown mode: {mode}")

    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <run.json>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    return verify_file(path)


if __name__ == "__main__":
    raise SystemExit(main())
