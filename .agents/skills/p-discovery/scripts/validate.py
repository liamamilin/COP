#!/usr/bin/env python3
"""Check the portable P Discovery output contract.

The validator checks structure, evidence quotations, and cross-references.
It cannot determine whether source claims are factually correct or whether a
quotation truly supports the P. Such review remains a separate quality gate.

This script intentionally uses Python's standard library only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

SUPPORTED_STATUSES = {"proposed", "source_supported", "reviewed"}
AVAILABILITIES = {"core", "extension", "unknown"}


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Root must be a JSON object"]
    if data.get("schema_version") != "0.1":
        errors.append("schema_version must be 0.1")
    topic = data.get("topic")
    if not isinstance(topic, dict) or not all(
        nonempty(topic.get(key)) for key in ("name", "scope")
    ):
        errors.append("topic must contain nonempty name and scope")
    for key in ("sources", "groups", "possibilities", "coverage_gaps"):
        if not isinstance(data.get(key), list):
            errors.append(f"{key} must be a list")

    if errors and any(not isinstance(data.get(k), list) for k in
                      ("sources", "groups", "possibilities", "coverage_gaps")):
        return errors

    sources: dict[str, dict] = {}
    groups: dict[str, dict] = {}
    possibilities: dict[str, dict] = {}
    all_ids: set[str] = set()

    for field, sink in (
        ("sources", sources),
        ("groups", groups),
        ("possibilities", possibilities),
    ):
        for index, item in enumerate(data[field]):
            loc = f"{field}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{loc} must be an object")
                continue
            item_id = item.get("id")
            if not nonempty(item_id):
                errors.append(f"{loc}.id must be a nonempty string")
                continue
            if item_id in all_ids:
                errors.append(f"Duplicate ID: {item_id} ({loc})")
            else:
                all_ids.add(item_id)
            sink[item_id] = item

    for source_id, source in sources.items():
        if not nonempty(source.get("title")):
            errors.append(f"Source {source_id}: missing title")
        url = source.get("url")
        parsed = urlparse(url) if isinstance(url, str) else None
        if not parsed or parsed.scheme not in ("http", "https") or not parsed.netloc:
            errors.append(f"Source {source_id}: invalid http(s) URL")
        if not nonempty(source.get("evidence")):
            errors.append(f"Source {source_id}: missing captured evidence")

    for group_id, group in groups.items():
        if not nonempty(group.get("name")):
            errors.append(f"Group {group_id}: missing name")

    for possibility_id, p in possibilities.items():
        for field in ("title", "result"):
            if not nonempty(p.get(field)):
                errors.append(f"P {possibility_id}: missing {field}")
        status = p.get("status")
        if status not in SUPPORTED_STATUSES:
            errors.append(f"P {possibility_id}: invalid status {status!r}")
        availability = p.get("availability")
        if availability not in AVAILABILITIES:
            errors.append(f"P {possibility_id}: invalid availability {availability!r}")
        if availability == "extension" and not nonempty(p.get("conditions")):
            errors.append(f"P {possibility_id}: extension must name conditions")

        source_ids = p.get("source_ids")
        group_ids = p.get("group_ids")
        evidence_refs = p.get("evidence_refs", [])
        for field, refs, allowed in (
            ("source_ids", source_ids, sources),
            ("group_ids", group_ids, groups),
        ):
            if not isinstance(refs, list) or not all(nonempty(ref) for ref in refs):
                errors.append(f"P {possibility_id}: {field} must be a list of IDs")
                continue
            if len(refs) != len(set(refs)):
                errors.append(f"P {possibility_id}: duplicate {field}")
            for ref in refs:
                if ref not in allowed:
                    errors.append(f"P {possibility_id}: unknown {field} {ref!r}")

        if not isinstance(evidence_refs, list):
            errors.append(f"P {possibility_id}: evidence_refs must be a list")
            evidence_refs = []

        if status in {"source_supported", "reviewed"} and not evidence_refs:
            errors.append(f"P {possibility_id}: confirmed P needs claim-specific evidence_refs")
        if status == "reviewed" and not nonempty(p.get("reviewed_by")):
            errors.append(f"P {possibility_id}: reviewed status needs human reviewed_by")

        for index, ref in enumerate(evidence_refs):
            loc = f"P {possibility_id}: evidence_refs[{index}]"
            if not isinstance(ref, dict):
                errors.append(f"{loc} must be an object")
                continue
            ref_id, quote = ref.get("source_id"), ref.get("quote")
            if not nonempty(ref_id) or ref_id not in sources:
                errors.append(f"{loc} references unknown source {ref_id!r}")
                continue
            if not isinstance(source_ids, list) or ref_id not in source_ids:
                errors.append(f"{loc} must also appear in source_ids")
            if not nonempty(quote):
                errors.append(f"{loc} missing verbatim quote")
            elif quote not in str(sources[ref_id].get("evidence", "")):
                errors.append(f"{loc} quote not present in captured source excerpt")

    gaps = data.get("coverage_gaps", [])
    if not all(isinstance(gap, str) for gap in gaps):
        errors.append("coverage_gaps must contain only strings")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 validate.py path/to/possibilities.json")
        return 2
    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read valid JSON from {path}: {exc}")
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: {path} (structural/evidence checks only; assess sources manually)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
