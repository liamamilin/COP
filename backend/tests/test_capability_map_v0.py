"""Schema and graph-integrity gates for the experimental P-C-O capability map."""

import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from app.domain.capability_map_v0 import graph_issues

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads(
    (ROOT / "schemas" / "cop-capability-map-v0.schema.json").read_text(encoding="utf-8")
)
FIXTURE_NAMES = (
    "capability-map-ggplot2-v0.json",
    "capability-map-langchain-v0.json",
)


def read_fixture(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


def test_capability_map_schema_itself_is_valid() -> None:
    Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("filename", FIXTURE_NAMES)
def test_capability_map_fixture_has_valid_schema_and_links(filename: str) -> None:
    doc = read_fixture(filename)
    Draft202012Validator(SCHEMA).validate(doc)
    assert graph_issues(doc) == []


def test_capability_map_rejects_step_as_replacement_for_possibility_outcome() -> None:
    doc = deepcopy(read_fixture(FIXTURE_NAMES[0]))
    doc["possibilities"][0]["outcome"] = ""
    assert not Draft202012Validator(SCHEMA).is_valid(doc)


def test_capability_map_finds_dangling_endpoint() -> None:
    doc = deepcopy(read_fixture(FIXTURE_NAMES[0]))
    doc["relations"][0]["to_id"] = "c_absent"
    assert any("INVALID_RELATION_ENDPOINTS" in issue for issue in graph_issues(doc))


def test_capability_map_finds_invalid_relation_types_for_endpoints() -> None:
    doc = deepcopy(read_fixture(FIXTURE_NAMES[0]))
    doc["relations"][0]["type"] = "acts_on"
    assert any("INVALID_RELATION_ENDPOINTS" in issue for issue in graph_issues(doc))


def test_capability_map_requires_both_c_and_o_for_each_p() -> None:
    doc = deepcopy(read_fixture(FIXTURE_NAMES[0]))
    doc["relations"] = [
        r
        for r in doc["relations"]
        if not (r["from_id"] == "p_groups" and r["type"] == "enabled_by")
    ]
    assert "P_MISSING_OPERATION: p_groups" in graph_issues(doc)


def test_capability_map_finds_invalid_source_reference() -> None:
    doc = deepcopy(read_fixture(FIXTURE_NAMES[1]))
    doc["operations"][0]["evidence_refs"] = [{"source_id": "not_real"}]
    assert any("UNKNOWN_SOURCE" in issue for issue in graph_issues(doc))


def test_capability_map_rejects_candidate_as_verified_without_source() -> None:
    doc = deepcopy(read_fixture(FIXTURE_NAMES[1]))
    doc["possibilities"][0]["evidence_refs"] = []
    assert any("MISSING_EVIDENCE_REF" in issue for issue in graph_issues(doc))
