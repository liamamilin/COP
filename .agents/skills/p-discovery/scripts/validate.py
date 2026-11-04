#!/usr/bin/env python3
"""Validate the small, host-neutral P Discovery JSON artifact.

This checks structure and cross-references, not factual correctness. No extra
packages, credentials, or vendor API required.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse


def validate(data: object) -> list[str]:
    problems: list[str] = []
    if not isinstance(data, dict):
        return ["Root must be a JSON object"]

    for key in ("topic", "sources", "groups", "possibilities", "coverage_gaps"):
        if key not in data:
            problems.append(f"Missing top-level key: {key}")
    if data.get("schema_version") != "0.1":
        problems.append("schema_version must be 0.1")

    topic = data.get("topic", {})
    if not isinstance(topic, dict) or not all(
        isinstance(topic.get(k), str) and topic[k].strip()
        for k in ("name", "scope")
    ):
        problems.append("topic.name and topic.scope are required strings")

    ids: dict[str, str] = {}
    kind_members: dict[str, set[str]] = {}
    for collection in ("sources", "groups", "possibilities"):
        items = data.get(collection, [])
        if not isinstance(items, list):
            problems.append(f"{collection} must be a list")
            continue
        kind_members[collection] = set()
        for i, item in enumerate(items):
            loc = f"{collection}[{i}]"
            if not isinstance(item, dict):
                problems.append(f"{loc} must be an object")
                continue
            uid = item.get("id")
            if not isinstance(uid, str) or not uid.strip():
                problems.append(f"{loc}.id must be a nonempty string")
                continue
            if uid in ids:
                problems.append(f"Duplicate ID {uid!r} in {ids[uid]} and {loc}")
            ids[uid] = loc
            kind_members[collection].add(uid)

    source_ids = kind_members.get("sources", set())
    group_ids = kind_members.get("groups", set())
    for source in data.get("sources", []) if isinstance(data.get("sources"), list) else []:
        if not isinstance(source, dict):
            continue
        if not isinstance(source.get("title"), str) or not source["title"].strip():
            problems.append(f"Source {source.get('id')!r}: missing title")
        url = source.get("url")
        if not isinstance(url, str) or urlparse(url).scheme not in ("http", "https"):
            problems.append(f"Source {source.get('id')!r}: invalid http(s) URL")
        if not isinstance(source.get("evidence"), str) or not source["evidence"].strip():
            problems.append(f"Source {source.get('id')!r}: missing evidence")

    for group in data.get("groups", []) if isinstance(data.get("groups"), list) else []:
        if isinstance(group, dict) and (
            not isinstance(group.get("name"), str) or not group["name"].strip()
        ):
            problems.append(f"Group {group.get('id')!r}: missing name")

    for p in (
        data.get("possibilities", [])
        if isinstance(data.get("possibilities"), list)
        else []
    ):
        if not isinstance(p, dict):
            continue
        pid = p.get("id", "?")
        for k in ("title", "result"):
            if not isinstance(p.get(k), str) or not p[k].strip():
                problems.append(f"P {pid!r}: missing {k}")
        status = p.get("status")
        if status not in ("proposed", "source_supported", "reviewed"):
            problems.append(f"P {pid!r}: invalid status {status!r}")
        availability = p.get("availability")
        if availability not in ("core", "extension", "unknown"):
            problems.append(f"P {pid!r}: invalid availability {availability!r}")
        for k, valid_ids in (("source_ids", source_ids), ("group_ids", group_ids)):
            refs = p.get(k)
            if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
                problems.append(f"P {pid!r}: {k} must be a list of IDs")
            else:
                for ref in refs:
                    if ref not in valid_ids:
                        problems.append(f"P {pid!r}: unknown {k} reference {ref!r}")
        if status in ("source_supported", "reviewed") and not p.get("source_ids"):
            problems.append(f"P {pid!r}: confirmed status requires source_ids")
        if availability == "extension" and not str(p.get("conditions", "")).strip():
            problems.append(f"P {pid!r}: extension requires conditions")

    gaps = data.get("coverage_gaps")
    if not isinstance(gaps, list) or not all(isinstance(g, str) for g in gaps):
        problems.append("coverage_gaps must be a list of strings")

    return problems


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
        print("\n".join(f"FAIL: {e}" for e in errors))
        return 1
    print(f"PASS: {path} (structural checks only; review sources separately)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
