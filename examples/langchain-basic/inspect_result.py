"""Inspect a saved invocation without creating an agent or spending another request."""

import argparse
import json
from pathlib import Path
from typing import Any


def validate_report(report: dict[str, Any]) -> str:
    mode = report.get("mode")
    if mode not in {"offline-fixture", "provider-response"}:
        raise ValueError("A construction-only record is not a completed invocation.")
    messages = report.get("messages")
    if not isinstance(messages, list) or len(messages) != 2:
        raise ValueError("Expected two messages in the completed, no-tool Basic profile.")
    if any(not isinstance(item, dict) for item in messages):
        raise ValueError("Every saved message must have a type and content.")
    if [item.get("type") for item in messages] != ["human", "ai"]:
        raise ValueError("Expected human -> ai, not merely the presence of an AI message.")
    if not isinstance(report.get("input"), str) or not report["input"].strip():
        raise ValueError("The report must identify a nonempty user input.")
    if messages[0].get("content") != report["input"]:
        raise ValueError("The saved user message does not match this run's input.")
    answer = messages[-1].get("content")
    if not isinstance(answer, str) or not answer.strip() or report.get("answer") != answer:
        raise ValueError("The reported answer must be the nonempty final AI message.")
    return mode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        with args.report.open(encoding="utf-8") as handle:
            report = json.load(handle)
        if not isinstance(report, dict):
            raise ValueError("The saved report must be a JSON object.")
        mode = validate_report(report)
    except (OSError, ValueError) as error:
        raise SystemExit(f"Inspection failed: {error}") from None
    print(f"mode: {mode}")
    print("message types: human -> ai")
    print(f"input: {report['input']}")
    print(f"answer: {report['answer']}")
    print("PASS: saved invocation shape and input/answer linkage; not a semantic answer grade.")
    if mode == "offline-fixture":
        print("LIVE PROVIDER AND LEARNER ACCEPTANCE: NOT VERIFIED")


if __name__ == "__main__":
    main()
