"""Deterministic integrity checks for the experimental capability-map artifact.

This is NOT the old Goal -> Process -> Stage artifact validator. Semantic
accuracy and source support still require human review.
"""

from typing import Any

RELATION_ENDPOINTS = {
    "requires_concept": ("possibility", "concept"),
    "enabled_by": ("possibility", "operation"),
    "acts_on": ("operation", "concept"),
    "related_to": ("concept", "concept"),
    "alternative_to": ("operation", "operation"),
}


def graph_issues(document: dict[str, Any]) -> list[str]:
    """Return actionable graph/evidence integrity issues (empty means structurally consistent).

    Assumes the document passed the JSON Schema first; this function handles
    relational invariants that JSON Schema alone cannot express.
    """
    issues: list[str] = []
    ids: dict[str, str] = {}
    sources = {str(s["id"]) for s in document.get("sources", [])}

    for kind, key in (
        ("source", "sources"),
        ("possibility", "possibilities"),
        ("concept", "concepts"),
        ("operation", "operations"),
        ("example", "examples"),
    ):
        for item in document.get(key, []):
            entity_id = str(item["id"])
            if entity_id in ids:
                issues.append(
                    f"DUPLICATE_ID: {entity_id} used as both {ids[entity_id]} and {kind}"
                )
            ids[entity_id] = kind

    if len(sources) != len(document.get("sources", [])):
        issues.append("DUPLICATE_SOURCE_ID")

    for collection in ("possibilities", "concepts", "operations", "relations", "examples"):
        for index, item in enumerate(document.get(collection, [])):
            location = f"{collection}[{index}]"
            refs = item.get("evidence_refs", [])
            if item.get("status") == "source_supported" and not refs:
                issues.append(f"MISSING_EVIDENCE_REF: {location}")
            for ref in refs:
                if ref["source_id"] not in sources:
                    issues.append(f"UNKNOWN_SOURCE: {location} -> {ref['source_id']}")

    coverage: dict[str, set[str]] = {
        p["id"]: set() for p in document.get("possibilities", [])
    }
    for index, relation in enumerate(document.get("relations", [])):
        kind = relation["type"]
        source_id, target_id = relation["from_id"], relation["to_id"]
        expected = RELATION_ENDPOINTS.get(kind)
        if expected is None:
            issues.append(f"INVALID_RELATION_TYPE: relations[{index}] -> {kind}")
            continue
        actual = (ids.get(source_id), ids.get(target_id))
        if actual != expected:
            issues.append(
                f"INVALID_RELATION_ENDPOINTS: relations[{index}] {source_id} -> "
                f"{target_id}; expected {expected}, found {actual}"
            )
        if actual == expected and kind == "requires_concept":
            coverage[source_id].add("concept")
        if actual == expected and kind == "enabled_by":
            coverage[source_id].add("operation")

    for possibility_id, links in coverage.items():
        if "concept" not in links:
            issues.append(f"P_MISSING_CONCEPT: {possibility_id}")
        if "operation" not in links:
            issues.append(f"P_MISSING_OPERATION: {possibility_id}")

    for example in document.get("examples", []):
        if ids.get(example["possibility_id"]) != "possibility":
            issues.append(f"INVALID_EXAMPLE_P: {example['id']}")
        for relation_key, expected_kind in (
            ("concept_ids", "concept"),
            ("operation_ids", "operation"),
        ):
            for ref_id in example[relation_key]:
                if ids.get(ref_id) != expected_kind:
                    issues.append(
                        f"INVALID_EXAMPLE_REF: {example['id']}.{relation_key} -> {ref_id}"
                    )
    return issues
