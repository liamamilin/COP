"""Explanatory structure, not a machine certificate of good teaching."""

import copy
import json
from pathlib import Path

from app.domain.learning_unit import LearningUnit, check_learning_unit, unit_manifest

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    return json.loads((ROOT / "fixtures" / name).read_text())


def example():
    artifact = load("langchain-basic-cop.json")
    unit = load("langchain-basic-learning-unit.json")
    refs = [step["stage_ref"] for step in unit["steps"]]
    unit["orientation"] = {
        "question": "How do we distinguish constructing an object from receiving an answer?",
        "why_this_route": "First identify the environment, then the inputs and execution.",
        "running_case": "A no-tool text request.",
        "case_facts": ["The script has a construction-only mode."],
        "case_unknowns": ["Whether a real provider will return a relevant answer."],
        "route": [
            {"stage_ref": ref, "question": f"What does {ref} establish?",
             "builds_on": refs[max(0, index - 1):index], "why_now": "Use the prior result.",
             "next_gap": "Execution and understanding still need separate evidence."}
            for index, ref in enumerate(refs)
        ],
    }
    for step in unit["steps"]:
        step["reasoning"] = [{
            "observation": "The observed output has a mode field.",
            "inference": "That mode limits what the output can establish.",
            "warrant": "Constructing and invoking are different operations.",
            "limitation": "This does not judge answer relevance.",
            "source_ids": [unit["sources"][0]["id"]],
        }]
    return unit, artifact


def issues(unit, artifact):
    return {item["code"] for item in check_learning_unit(unit, artifact)}


def test_legacy_unit_keeps_its_exact_saved_shape_and_binding():
    unit = load("langchain-basic-learning-unit.json")
    parsed = LearningUnit.model_validate(unit)
    assert parsed.orientation is None
    assert parsed.model_dump(mode="json", exclude_unset=True) == unit


def test_oriented_unit_roundtrip_has_no_inferred_prose_or_semantic_claim():
    unit, artifact = example()
    before = copy.deepcopy(unit)
    assert check_learning_unit(unit, artifact) == []
    assert LearningUnit.model_validate(unit).model_dump(mode="json", exclude_unset=True) == unit
    assert unit == before
    assert "semantic correctness" in unit_manifest(unit, artifact)["not_verified"]


def test_missing_reasoning_is_not_hidden_by_a_valid_method_or_nonempty_goal():
    unit, artifact = example()
    unit["steps"][1].pop("reasoning")
    assert "MISSING_REASONING" in issues(unit, artifact)


def test_route_explanation_must_match_the_actual_method_order():
    unit, artifact = example()
    unit["orientation"]["route"].reverse()
    assert "TEACHING_ROUTE" in issues(unit, artifact)


def test_prerequisite_cannot_be_future_self_unknown_or_duplicated():
    unit, artifact = example()
    for refs in ([unit["steps"][1]["stage_ref"]], [unit["steps"][0]["stage_ref"]], ["unknown"]):
        unit["orientation"]["route"][0]["builds_on"] = refs
        assert "TEACHING_PREREQUISITE" in issues(unit, artifact)
    unit, artifact = example()
    unit["orientation"]["route"][1]["builds_on"] *= 2
    assert "TEACHING_PREREQUISITE" in issues(unit, artifact)


def test_reasoning_citations_resolve_but_are_not_truth_certificates():
    unit, artifact = example()
    unit["steps"][0]["reasoning"][0]["source_ids"] = ["invented"]
    assert "REASONING_SOURCE" in issues(unit, artifact)


def test_communication_sample_is_a_complete_non_code_reasoning_path():
    unit = load("communication-basics-learning-unit.json")
    artifact = load("communication-basics-cop.json")
    assert check_learning_unit(unit, artifact) == []
    assert unit_manifest(unit, artifact) == load("communication-basics-learning-unit.manifest.json")
    assert unit["orientation"]["case_unknowns"]
    assert all(step["reasoning"] for step in unit["steps"])
    assert all(not detail.get("command") for stage in artifact["stages"]
               for detail in stage["implementation_details"])
    assert {question["kind"] for question in unit["assessment"]} >= {
        "explain", "diagnose", "transfer",
    }
