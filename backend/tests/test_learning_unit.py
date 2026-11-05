"""Contract rejection tests using a legitimate non-code teaching unit.

The checker must not be hardwired to programming. No candidate body is executed,
and no database, provider or network is used.
"""

import copy
import json
from pathlib import Path

from app.domain.learning_unit import check_learning_unit, content_hash, unit_manifest


def artifact():
    """A small but schema-valid COP about comparing two purchase offers."""
    return {
        "schema_version": "0.1",
        "artifact_id": "artifact.offer",
        "domain": {"name": "Offers", "scope": "Compare two offers", "target_user": "A beginner",
                   "non_goals": []},
        "mental_model": {"summary": "Compare total cost.", "flow": ["Compute", "Compare"]},
        "goals": [{"id": "goal.offer", "title": "Compare offers", "outcome": "A choice",
                   "why_it_matters": "", "prerequisite_goal_refs": [], "evidence_refs": []}],
        "shared_foundations": [],
        "main_processes": [{"id": "process.offer", "goal_ref": "goal.offer",
                            "title": "Compare", "start": {"type": "zero", "ref": None},
                            "stage_refs": ["stage.compare"], "outcome": "A reasoned choice",
                            "practice_ref": "practice.offer"}],
        "stages": [{
            "id": "stage.compare", "title": "Compare total cost", "local_goal": "Choose",
            "why_it_exists": "Unit price alone hides fees.", "local_outcome": "A choice",
            "concept_refs": ["concept.total"], "operation_refs": ["operation.compare"],
            "branch_refs": [], "evidence_refs": [],
            "implementation_details": [
                {"title": "Add the fee", "action": "Add each fixed fee to its subtotal.",
                 "command": "", "expected_result": "Two totals", "caution": "Use one currency."},
            ],
            "example": {"summary": "Two offers", "input": "A: 10+2, B: 11+0",
                        "output": "B", "note": "Illustration"},
        }],
        "concepts": [{"id": "concept.total", "name": "Total cost",
                      "definition": "Price plus fees.", "role": "Basis for comparison",
                      "related_concept_refs": [], "key_operation_refs": ["operation.compare"]}],
        "operations": [{"id": "operation.compare", "name": "Compare totals",
                        "definition": "Add and compare.", "purpose": "",
                        "acts_on_concept_refs": ["concept.total"], "common_failures": []}],
        "branches": [],
        "practices": [{"id": "practice.offer", "title": "Practice", "goal_ref": "goal.offer",
                       "instructions": ["Compare"], "expected_outcome": "A choice",
                       "checkpoint_questions": []}],
        "expansion_map": [],
        "metadata": {"language": "en", "generated_at": "", "generator": "", "source_ids": []},
    }


def question(identifier, kind, stages=None):
    return {"id": identifier, "kind": kind, "prompt": f"{kind} prompt", "hints": ["hint"],
            "criteria": ["criterion"], "stage_refs": stages or ["stage.compare"],
            "path_ids": []}


def lesson(source):
    return {
        "schema_version": "0.1-experimental",
        "unit_id": "unit.offer",
        "title": "Compare two offers",
        "outcome": "Choose and explain",
        "task_brief": "Compute both totals, then choose.",
        "binding": {"artifact_sha256": content_hash(source), "goal_ref": "goal.offer",
                    "process_ref": "process.offer"},
        "profile": {
            "audience": "A beginner", "prior_knowledge": ["Addition"],
            "environment": ["Paper"], "exclusions": ["No credit"],
            "resources": [{"id": "entry.numbers", "name": "Two offers",
                           "provenance": "Your own quotes", "readiness_check": "Read both",
                           "path_ids": []}],
        },
        "paths": [{"id": "main", "label": "Main", "description": "The whole task",
                   "goal_scope": "full", "needs_network": False, "may_cost": False}],
        "outputs": [{"id": "out.choice", "name": "Choice", "description": "A reasoned choice",
                     "producer_stage_ref": "stage.compare", "kind": "value",
                     "persistence": "durable", "format": "text", "content_ref": None,
                     "path_ids": []}],
        "steps": [{
            "stage_ref": "stage.compare", "purpose": "Choose the lower total",
            "inputs": [{"kind": "entry", "ref": "entry.numbers", "why_needed": "Inputs",
                        "readiness_check": "Both readable", "path_ids": []}],
            "concepts": [{"concept_ref": "concept.total", "plain_language": "Price plus fee",
                          "concrete_example": "10 + 2", "contrast": "Not list price",
                          "why_here": "Totals decide"}],
            "causal_chain": [{"concept_ref": "concept.total",
                              "operation_ref": "operation.compare", "before": "Two prices",
                              "action": "Add fees", "because": "Fees change rank",
                              "after": "A lower total"}],
            "methods": [{"detail_index": 0, "teaching_note": "Add once",
                         "optional": False, "path_ids": []}],
            "output_refs": ["out.choice"],
            "worked_case": {"kind": "illustration", "input_refs": ["entry.numbers"],
                            "output_refs": ["out.choice"],
                            "walkthrough": ["10+2=12", "11+0=11"], "observation": "B is lower"},
            "checks": [{"output_ref": "out.choice", "instruction": "Re-add",
                        "expected": "B", "why": "Fees matter", "limitation": "One example",
                        "on_failure": "Recheck arithmetic", "path_ids": []}],
            "practice": question("q.practice", "predict"),
        }],
        "assessment": [question("q.explain", "explain"), question("q.diagnose", "diagnose"),
                       question("q.transfer", "transfer")],
        "sources": [{"id": "src", "title": "Quotes", "url": "https://example.com",
                     "scope": "Illustration only"}],
        "limitations": ["Only two offers."],
    }


def codes(raw, source=None):
    return {item["code"] for item in check_learning_unit(raw, source or artifact())}


def test_valid_non_code_unit_round_trips_and_manifest_is_honest():
    source = artifact()
    raw = lesson(source)
    assert check_learning_unit(raw, source) == []
    serialized = json.loads(json.dumps(raw))
    assert check_learning_unit(serialized, source) == []
    manifest = unit_manifest(raw, source)
    assert manifest["scope"] == "structure-and-bindings-only"
    assert manifest["unit_sha256"] == content_hash(raw)
    assert manifest["artifact_sha256"] == content_hash(source)
    assert manifest["issues"] == []
    assert set(manifest["not_verified"]) >= {"semantic correctness", "live execution",
                                             "learner understanding", "transfer performance"}


def test_hash_is_stable_across_key_order_but_not_array_order_or_content():
    source = artifact()
    assert content_hash(dict(reversed(list(source.items())))) == content_hash(source)
    changed = copy.deepcopy(source)
    changed["stages"][0]["implementation_details"][0]["action"] = "Different"
    assert content_hash(changed) != content_hash(source)
    changed["goals"] = list(reversed(changed["goals"]))
    assert content_hash(changed) != content_hash(source)


def test_stale_teaching_and_invalid_artifact_are_rejected():
    source = artifact()
    raw = lesson(source)
    changed = copy.deepcopy(source)
    changed["goals"][0]["outcome"] = "A different artifact"
    assert "STALE_ARTIFACT" in codes(raw, changed)
    broken = copy.deepcopy(source)
    broken["stages"][0]["concept_refs"] = ["concept.missing"]
    assert codes(raw, broken)


def test_unresolved_target_route_order_and_duplicates_are_rejected():
    source = artifact()
    raw = lesson(source)
    raw["binding"]["process_ref"] = "process.missing"
    assert "UNIT_TARGET" in codes(raw, source)
    raw = lesson(source)
    raw["steps"].append(copy.deepcopy(raw["steps"][0]))
    result = codes(raw, source)
    assert {"UNIT_ROUTE", "DUPLICATE_STAGE"} <= result
    raw = lesson(source)
    raw["steps"][0]["output_refs"] = ["out.unknown"]
    assert "OUTPUT_REF" in codes(raw, source)
    raw = lesson(source)
    raw["steps"][0]["output_refs"].append("out.choice")
    assert "DUPLICATE_OUTPUT" in codes(raw, source)


def test_missing_forward_and_ephemeral_handoffs_are_rejected():
    source = artifact()
    source["main_processes"][0]["stage_refs"] = ["stage.compare", "stage.second"]
    source["stages"].append({
        "id": "stage.second", "title": "Second", "local_goal": "Continue",
        "why_it_exists": "", "local_outcome": "Done", "concept_refs": ["concept.total"],
        "operation_refs": ["operation.compare"], "branch_refs": [], "evidence_refs": [],
        "implementation_details": [{"title": "Write", "action": "Use the result"}],
        "example": None,
    })
    raw = lesson(source)
    second = copy.deepcopy(raw["steps"][0])
    second["stage_ref"] = "stage.second"
    second["practice"]["id"] = "q.second"
    second["practice"]["stage_refs"] = ["stage.second"]
    second["inputs"] = [{"kind": "output", "ref": "out.choice", "why_needed": "Next",
                         "readiness_check": "Exists", "path_ids": []}]
    second["worked_case"]["input_refs"] = ["out.choice"]
    second["output_refs"] = []
    second["worked_case"]["output_refs"] = []
    second["checks"] = []
    raw["outputs"].append({
        "id": "out.second", "name": "Second choice", "description": "The next result",
        "producer_stage_ref": "stage.second", "kind": "value", "persistence": "durable",
        "format": "text", "content_ref": None, "path_ids": [],
    })
    second["output_refs"] = ["out.second"]
    second["worked_case"]["output_refs"] = ["out.second"]
    second["checks"] = [{
        "output_ref": "out.second", "instruction": "Check", "expected": "Done",
        "why": "Result", "limitation": "Not semantics", "on_failure": "Retry",
        "path_ids": [],
    }]
    raw["steps"].append(second)
    assert check_learning_unit(raw, source) == []

    forward = copy.deepcopy(raw)
    forward["steps"][0]["inputs"].append({
        "kind": "output", "ref": "out.choice", "why_needed": "Uses a later result",
        "readiness_check": "Exists", "path_ids": [],
    })
    forward["steps"][0]["worked_case"]["input_refs"].append("out.choice")
    assert "FORWARD_INPUT" in codes(forward, source)

    ephemeral = copy.deepcopy(raw)
    ephemeral["outputs"][0]["persistence"] = "process"
    assert "EPHEMERAL_HANDOFF" in codes(ephemeral, source)

    missing = copy.deepcopy(raw)
    missing["steps"][1]["inputs"][0]["ref"] = "out.nowhere"
    missing["steps"][1]["worked_case"]["input_refs"] = ["out.nowhere"]
    assert "MISSING_INPUT" in codes(missing, source)


def test_files_need_resolvable_parseable_content_without_execution(tmp_path):
    source = artifact()
    stage = source["stages"][0]
    stage["implementation_details"].append({
        "title": "Save data", "action": "Save it", "command": "",
    })
    raw = lesson(source)
    raw["outputs"].append({
        "id": "out.file", "name": "data.json", "description": "A file",
        "producer_stage_ref": "stage.compare", "kind": "file", "persistence": "durable",
        "format": "json", "content_ref": {"stage_ref": "stage.compare", "detail_index": 1},
        "path_ids": [],
    })
    raw["steps"][0]["output_refs"].append("out.file")
    raw["steps"][0]["methods"].append({
        "detail_index": 1, "teaching_note": "Save", "optional": False, "path_ids": [],
    })
    raw["steps"][0]["worked_case"]["output_refs"].append("out.file")
    raw["steps"][0]["checks"].append({
        "output_ref": "out.file", "instruction": "Parse", "expected": "JSON",
        "why": "Structure", "limitation": "Not semantics", "on_failure": "Rewrite",
        "path_ids": [],
    })
    assert "MISSING_FILE_CONTENT" in codes(raw, source)

    stage["implementation_details"][1]["command"] = '{"ok": true}'
    raw["binding"]["artifact_sha256"] = content_hash(source)
    assert check_learning_unit(raw, source) == []

    stage["implementation_details"][1]["command"] = "def broken("
    raw["binding"]["artifact_sha256"] = content_hash(source)
    assert "INVALID_FILE_CONTENT" in codes(raw, source)

    side_effect = tmp_path / "should-not-exist"
    stage["implementation_details"][1]["command"] = (
        f"open({str(side_effect)!r}, 'w').write('executed')"
    )
    raw["binding"]["artifact_sha256"] = content_hash(source)
    assert "INVALID_FILE_CONTENT" in codes(raw, source)
    assert not side_effect.exists()

    raw["outputs"][-1]["kind"] = "private"
    assert "PRIVATE_CONTENT" in codes(raw, source)


def test_paths_inputs_methods_checks_and_practice_are_covered():
    source = artifact()
    raw = lesson(source)
    raw["paths"].append({"id": "extra", "label": "Extra", "description": "Another route",
                         "goal_scope": "partial", "needs_network": False, "may_cost": False})
    raw["steps"][0]["inputs"][0]["path_ids"] = ["main"]
    raw["steps"][0]["methods"][0]["path_ids"] = ["main"]
    raw["outputs"][0]["path_ids"] = ["main"]
    raw["steps"][0]["practice"]["path_ids"] = ["main"]
    assert "STEP_INPUT_GAP" in codes(raw, source)
    assert "STEP_METHOD_GAP" in codes(raw, source)
    assert "STEP_OUTPUT_GAP" in codes(raw, source)
    assert "PRACTICE_PATH_GAP" in codes(raw, source)

    raw = lesson(source)
    raw["steps"][0]["methods"][0]["path_ids"] = ["unknown"]
    assert "UNKNOWN_PATH" in codes(raw, source)

    raw = lesson(source)
    raw["steps"][0]["methods"][0]["detail_index"] = 9
    assert "METHOD_REF" in codes(raw, source)
    raw["steps"][0]["methods"][0]["detail_index"] = 0
    source = artifact()
    source["stages"][0]["implementation_details"][0]["action"] = ""
    source["stages"][0]["implementation_details"][0]["command"] = ""
    raw = lesson(source)
    assert "EMPTY_METHOD" in codes(raw, source)

    raw = lesson(artifact())
    raw["steps"][0]["checks"] = [{
        "output_ref": "out.unknown", "instruction": "Wrong target", "expected": "x",
        "why": "x", "limitation": "x", "on_failure": "x", "path_ids": [],
    }]
    assert "UNCHECKED_OUTPUT" in codes(raw)


def test_concept_operation_and_example_links_are_checked():
    source = artifact()
    raw = lesson(source)
    raw["steps"][0]["concepts"][0]["concept_ref"] = "concept.unknown"
    assert "CONCEPT_REF" in codes(raw, source)
    raw = lesson(source)
    raw["steps"][0]["causal_chain"][0]["operation_ref"] = "operation.unknown"
    assert "CAUSAL_REF" in codes(raw, source)
    raw = lesson(source)
    raw["steps"][0]["causal_chain"][0]["concept_ref"] = "concept.unknown"
    assert "CAUSAL_REF" in codes(raw, source)
    raw = lesson(source)
    raw["steps"][0]["worked_case"]["input_refs"] = ["entry.unknown"]
    assert "EXAMPLE_INPUT" in codes(raw, source)
    raw = lesson(source)
    raw["steps"][0]["worked_case"]["output_refs"] = ["out.unknown"]
    assert "EXAMPLE_OUTPUT" in codes(raw, source)
    raw = lesson(source)
    raw["steps"][0]["concepts"].append(copy.deepcopy(raw["steps"][0]["concepts"][0]))
    assert "DUPLICATE_CONCEPT" in codes(raw, source)


def test_assessment_requires_explain_diagnose_transfer_on_every_path():
    source = artifact()
    raw = lesson(source)
    raw["assessment"] = [question("a", "predict"), question("b", "explain"),
                         question("c", "transfer")]
    assert "ASSESSMENT_GAP" in codes(raw, source)
    raw["assessment"] = [question("a", "explain"), question("b", "diagnose"),
                         question("c", "transfer")]
    assert check_learning_unit(raw, source) == []
    raw["assessment"][2]["path_ids"] = []
    raw["assessment"][2]["stage_refs"] = ["stage.missing"]
    assert "QUESTION_REF" in codes(raw, source)
    raw = lesson(source)
    raw["assessment"][0]["id"] = raw["steps"][0]["practice"]["id"]
    assert "DUPLICATE_QUESTION" in codes(raw, source)


def test_duplicate_entry_and_output_ids_are_rejected():
    source = artifact()
    raw = lesson(source)
    raw["outputs"][0]["id"] = "entry.numbers"
    result = codes(raw, source)
    assert {"DUPLICATE_ID", "MISSING_PRODUCER"} <= result
    raw = lesson(source)
    raw["steps"][0]["inputs"][0]["ref"] = "out.missing"
    raw["steps"][0]["worked_case"]["input_refs"] = ["out.missing"]
    assert "MISSING_INPUT" in codes(raw, source)


def test_repository_basic_fixture_is_bound_and_manifest_matches():
    root = Path(__file__).resolve().parents[2]
    unit = json.loads((root / "fixtures/langchain-basic-learning-unit.json").read_text())
    source = json.loads((root / "fixtures/langchain-basic-cop.json").read_text())
    manifest = json.loads(
        (root / "fixtures/langchain-basic-learning-unit.manifest.json").read_text()
    )
    assert check_learning_unit(unit, source) == []
    assert manifest == unit_manifest(unit, source)
    assert unit["binding"]["artifact_sha256"] == content_hash(source)
