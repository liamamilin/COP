#!/usr/bin/env python3
"""Validate Topic Registry and derive a safe research queue from current data."""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATES = {"candidate", "eligible", "researching", "review", "rework", "accepted",
          "published", "researched_in_unmerged_pr", "blocked"}
IDENTITY = {"unverified", "source_checked", "existing_research", "ambiguous"}
TRANSITIONS = {
    "candidate": {"eligible", "blocked"},
    "eligible": {"researching", "blocked", "candidate"},
    "researching": {"review", "rework", "blocked"},
    "review": {"accepted", "rework", "blocked"},
    "rework": {"researching", "blocked"},
    "accepted": {"published", "rework"},
    "published": set(),
    "researched_in_unmerged_pr": {"accepted", "published", "rework"},
    "blocked": {"candidate", "eligible"},
}

def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def require(condition: bool, message: str):
    if not condition:
        raise ValueError(message)

def validate(tax: dict, registry: dict) -> dict:
    require(tax.get("schema_version") == registry.get("schema_version") == "0.4",
            "Incompatible schema versions")
    domains = {d["id"]: d for d in tax["domains"]}
    areas = {a["id"]: a for a in tax["areas"]}
    require(len(domains) == len(tax["domains"]), "Duplicate domains")
    require(len(areas) == len(tax["areas"]), "Duplicate areas")
    for area in areas.values():
        require(area["domain_id"] in domains, f"Orphan area {area['id']}")
        require(area["coverage_state"] in
                {"taxonomy_seeded_not_exhaustive", "unseeded_needs_discovery",
                 "source_survey_in_progress", "source_survey_completed"},
                f"Unknown coverage state {area['id']}")
    topics = {}
    counts = Counter()
    for topic in registry["items"]:
        slug = topic["slug"]
        require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) is not None,
                f"Invalid slug {slug}")
        require(slug not in topics, f"Duplicate topic slug {slug}")
        topics[slug] = topic
        area_id = topic["area_id"]
        require(area_id in areas, f"Orphan topic {slug}")
        require(topic["domain_id"] == areas[area_id]["domain_id"],
                f"Wrong parent {slug}")
        require(bool(topic.get("title", "").strip()) and
                bool(topic.get("description", "").strip()), f"Empty topic {slug}")
        require(topic["scope_level"] in {"bounded_subject", "area_survey"},
                f"Wrong scope level {slug}")
        state = topic["research_state"]
        selection = topic.get("selection_status", state)
        require(state in STATES, f"Unknown research state {slug}: {state}")
        require(selection in STATES | {"already_researched"},
                f"Invalid selection status {slug}")
        require(topic.get("identity_status") in IDENTITY,
                f"Unknown identity status {slug}")
        if selection == "eligible":
            require(state == "candidate", f"Eligible non-candidate {slug}")
            require(topic["scope_level"] == "bounded_subject",
                    f"Area survey eligible {slug}")
            require(topic["identity_status"] == "source_checked",
                    f"Unverified identity eligible {slug}")
            require(re.match(r"^https://", topic.get("official_url") or ""),
                    f"No official source for eligible {slug}")
        if state == "blocked":
            require(selection == "blocked", f"Blocked item selectable: {slug}")
        counts[area_id] += 1
    for area in areas.values():
        if counts[area["id"]] == 0:
            require(area["coverage_state"] == "unseeded_needs_discovery",
                    f"Unseeded area misrepresented: {area['id']}")
        else:
            require(area["coverage_state"] != "unseeded_needs_discovery",
                    f"Seeded area marked empty: {area['id']}")
    for topic in topics.values():
        slug = topic["slug"]
        for other in topic.get("related_topics", []):
            require(other in topics and other != slug, f"Bad relation {slug} -> {other}")
        require(len(topic.get("related_topics", [])) ==
                len(set(topic.get("related_topics", []))),
                f"Repeated relation {slug}")
    return topics

def build_queue(registry: dict, topics: dict, previous: dict) -> dict:
    order = []
    group = {}
    for wave in previous.get("waves", []):
        for slug in wave.get("topic_slugs", []):
            require(slug not in group, f"Repeated wave assignment {slug}")
            require(slug in topics, f"Unknown wave topic {slug}")
            group[slug] = wave["id"]
            order.append(slug)
    executable = []
    deferred = []
    def ready(t: dict) -> bool:
        return (t.get("selection_status") == "eligible" and
                t["research_state"] == "candidate" and
                t["scope_level"] == "bounded_subject" and
                t.get("identity_status") == "source_checked" and
                bool(re.match(r"^https://", t.get("official_url") or "")))
    for slug in order + sorted(set(topics) - set(order)):
        t = topics[slug]
        if t["research_state"] not in {"candidate", "eligible", "blocked", "rework"}:
            continue
        if ready(t):
            executable.append({
                "slug": slug, "source_wave": group.get(slug),
                "official_url": t["official_url"], "area_id": t["area_id"]
            })
        elif slug in group:
            deferred.append({
                "slug": slug, "source_wave": group[slug],
                "reason": "identity_or_scope_not_approved" if t["research_state"] != "blocked"
                          else "blocked"
            })
    return {
        "schema_version": "0.4",
        "source_registry": "catalog/topic-registry.v0.4.json",
        "state": "generated_not_running",
        "max_parallel_global": previous.get("max_parallel_global", 2),
        "executable": executable,
        "deferred_preferred": deferred,
        "planned_wave_definitions": previous.get("waves", []),
        "policy": "Only eligible, identity-checked bounded subjects enter executable. No automatic research or publication."
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-queue", action="store_true",
                        help="Update queue file with eligibility derived from registry")
    parser.add_argument("--check-transition", nargs=3,
                        metavar=("SLUG", "FROM", "TO"),
                        help="Validate a lifecycle state change; does not write data")
    args = parser.parse_args()
    tax = load("catalog/topic-taxonomy.v0.4.json")
    reg = load("catalog/topic-registry.v0.4.json")
    existing = load("catalog/research-queue.v0.4.json")
    topics = validate(tax, reg)
    if args.check_transition:
        slug, old, new = args.check_transition
        require(slug in topics, f"Unknown topic {slug}")
        require(old in TRANSITIONS and new in TRANSITIONS[old],
                f"Disallowed transition {old} -> {new}")
        print(f"PASS transition {slug}: {old} -> {new}")
        return
    queue = build_queue(reg, topics, existing)
    if args.write_queue:
        (ROOT / "catalog/research-queue.v0.4.json").write_text(
            json.dumps(queue, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
    else:
        # If queue has already been generated, detect stale material.
        if "executable" in existing:
            require(existing == queue, "Stale queue: run --write-queue")
    counts = Counter(t["research_state"] for t in topics.values())
    print(f"PASS {len(tax['domains'])} domains, {len(tax['areas'])} areas, "
          f"{len(topics)} topics; states {dict(counts)}")
    print(f"PASS {len(queue['executable'])} eligible subjects, "
          f"{len(queue['deferred_preferred'])} deferred priority suggestions")
    print("LIMIT: identity source checks do not prove P quality or domain completeness")

if __name__ == "__main__":
    main()
