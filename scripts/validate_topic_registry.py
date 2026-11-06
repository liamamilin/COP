#!/usr/bin/env python3
"""Validate COP v0.4 Topic Registry / taxonomy / research queue without external services."""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT / p).read_text(encoding="utf-8"))
def need(v, msg):
    if not v: raise ValueError(msg)
def unique(items, kind):
    ids = [x["id"] for x in items]
    need(len(ids) == len(set(ids)), f"duplicate {kind}")
def main():
    tx = load("catalog/topic-taxonomy.v0.4.json")
    reg = load("catalog/topic-registry.v0.4.json")
    queue = load("catalog/research-queue.v0.4.json")
    need(tx["schema_version"] == reg["schema_version"] == queue["schema_version"] == "0.4", "schema version")
    unique(tx["domains"], "domain")
    unique(tx["areas"], "area")
    domains = {x["id"] for x in tx["domains"]}
    areas = {x["id"]: x for x in tx["areas"]}
    slugs = [x["slug"] for x in reg["items"]]
    need(len(slugs) == len(set(slugs)), "duplicate topic slug")
    need(all(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", s) for s in slugs), "invalid topic slug")
    topics = {x["slug"]: x for x in reg["items"]}
    ctr = Counter()
    for a in tx["areas"]:
        need(a["domain_id"] in domains, f"bad area parent: {a['id']}")
        need(a["coverage_state"] == "taxonomy_seeded_not_exhaustive", "misleading coverage claim")
    for t in topics.values():
        need(t["area_id"] in areas, f"unknown area: {t['slug']}")
        need(t["domain_id"] == areas[t["area_id"]]["domain_id"], f"wrong topic parent: {t['slug']}")
        need(bool(t["title"].strip()) and bool(t["description"].strip()), "blank topic")
        need(t["scope_level"] in ("bounded_subject", "area_survey"), f"bad level: {t['slug']}")
        need(t["research_state"] in ("published", "researched_in_unmerged_pr", "candidate"), "bad research state")
        if t["research_state"] == "candidate":
            need(t["selection_status"] == "candidate" and t["evidence_status"] == "not_topic_verified", "candidate falsely marked reviewed")
        ctr[t["area_id"]] += 1
    need(all(ctr[id_] >= 1 for id_ in areas), "at least one area has no seed subjects")
    provenance = Counter(t["origin"] for t in topics.values())
    need(provenance == {"atlas_main": 20, "atlas_v0.2_pr": 18, "prior_v0.3_backlog": 72, "taxonomy_seed_curated": 181}, f"unexpected provenance: {provenance}")
    qslugs = []
    for wave in queue["waves"]:
        need(wave["max_parallel"] <= queue["max_parallel_global"] and wave["max_parallel"] >= 1, "invalid concurrency")
        need(wave["state"] == "proposed_not_started", "wave marked started")
        for slug in wave["topic_slugs"]:
            need(slug in topics, f"queue missing topic {slug}")
            need(topics[slug]["research_state"] == "candidate", f"queue already researched: {slug}")
            need(topics[slug]["scope_level"] == "bounded_subject", f"queue uses area survey: {slug}")
            qslugs.append(slug)
    need(len(qslugs) == len(set(qslugs)), "queued topic repeated")
    main_catalog = load("catalog/p-atlas-topics.v0.1.json")
    main_slugs = {x["slug"] for x in main_catalog["topics"]}
    need(main_slugs == {x["slug"] for x in topics.values() if x["origin"] == "atlas_main"}, "main catalog reconciliation mismatch")
    print(f"PASS: {len(domains)} domains, {len(areas)} areas (all seeded), {len(topics)} topics.")
    print(f"PASS: provenance {dict(provenance)}; proposed research waves {len(queue['waves'])}, {len(qslugs)} queued topics.")
    print("LIMIT: taxonomy seed coverage is not an exhaustive source-based ecosystem audit.")
if __name__ == "__main__": main()
