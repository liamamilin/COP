"""Offline identity, reference, and cross-batch registry regressions for H60."""

from copy import deepcopy
from typing import Any

import pytest

from app.core.errors import HarnessError
from app.harness.context import HarnessContext
from app.harness.prompts import decode_payload
from app.harness.steps.h60_canonicalize import (
    CANONICALIZE_BATCH_SIZE,
    MAX_CANONICALIZE_PROMPT_CHARS,
    MAX_CONCEPT_CANDIDATES,
    REGISTRY_DEFINITION_LENGTH,
    CanonicalizeStep,
    merge_canonicalization_payloads,
)


def concept(key: str, name: str, **fields: Any) -> dict[str, Any]:
    return {"key": key, "name": name, "definition": f"Definition of {name}",
            "role": "r", **fields}


def operation(key: str, name: str, **fields: Any) -> dict[str, Any]:
    return {"key": key, "name": name, "definition": f"Definition of {name}",
            "purpose": "p", **fields}


def payload(
    concepts: list[dict[str, Any]], operations: list[dict[str, Any]],
    stage_key: str | None = None,
) -> dict[str, Any]:
    return {
        "concepts": concepts, "operations": operations,
        "stage_bindings": {
            stage_key: {"concept_keys": [item["key"] for item in concepts],
                        "operation_keys": [item["key"] for item in operations]}
        } if stage_key is not None else {},
    }


def test_multiple_concept_and_operation_maps_survive_two_colliding_batches():
    batches = [
        payload(
            [concept("a", first, related_concept_keys=["b"], key_operation_keys=["x", "y"]),
             concept("b", second, related_concept_keys=["a"], key_operation_keys=["y"])],
            [operation("x", do_first, acts_on_concept_keys=["a", "b"]),
             operation("y", do_second, acts_on_concept_keys=["b"])],
            stage_key,
        )
        for first, second, do_first, do_second, stage_key in (
            ("Noise", "Feedback", "Filter", "Respond", "s1"),
            ("Runtime", "Memory", "Allocate", "Release", "s2"),
        )
    ]
    merged = merge_canonicalization_payloads(batches, warnings=[])
    for offset, stage_key in ((0, "s1"), (2, "s2")):
        first, second = merged["concepts"][offset:offset + 2]
        op1, op2 = merged["operations"][offset:offset + 2]
        assert first["related_concept_keys"] == [second["key"]]
        assert second["related_concept_keys"] == [first["key"]]
        assert first["key_operation_keys"] == [op1["key"], op2["key"]]
        assert second["key_operation_keys"] == [op2["key"]]
        assert op1["acts_on_concept_keys"] == [first["key"], second["key"]]
        assert op2["acts_on_concept_keys"] == [second["key"]]
        assert merged["stage_bindings"][stage_key] == {
            "concept_keys": [first["key"], second["key"]],
            "operation_keys": [op1["key"], op2["key"]],
        }


def test_same_names_with_different_keys_preserve_all_entities_and_references():
    batches = [
        payload(
            [concept("vm", "Runtime", definition="Host virtual machine")],
            [operation("vm_run", "Run", acts_on_concept_keys=["vm"])], "s1",
        ),
        payload(
            [concept("loop", "Runtime", definition="Execution loop",
                     related_concept_keys=["vm"], key_operation_keys=["loop_run"])],
            [operation("loop_run", "Run", definition="Start loop",
                       acts_on_concept_keys=["loop", "vm"])], "s2",
        ),
    ]
    before = deepcopy(batches)
    notices: list[str] = []
    merged = merge_canonicalization_payloads(batches, warnings=notices)
    assert [item["key"] for item in merged["concepts"]] == ["vm", "loop"]
    assert [item["key"] for item in merged["operations"]] == ["vm_run", "loop_run"]
    assert merged["concepts"][1]["related_concept_keys"] == ["vm"]
    assert merged["concepts"][1]["key_operation_keys"] == ["loop_run"]
    assert merged["operations"][1]["acts_on_concept_keys"] == ["loop", "vm"]
    assert merged["stage_bindings"]["s2"]["concept_keys"] == ["loop"]
    assert len(notices) == 2
    assert batches == before, "merging must not mutate saved provider responses"


def test_reused_identity_accumulates_relations_from_every_batch():
    shared = concept("runtime", "Runtime")
    op = operation("run", "Run", acts_on_concept_keys=["runtime"])
    batches = [
        payload([shared], [op], "s1"),
        payload(
            [{**shared, "related_concept_keys": ["memory"], "key_operation_keys": ["run", "free"]},
             concept("memory", "Memory", key_operation_keys=["free"])],
            [{**op, "acts_on_concept_keys": ["runtime", "memory"]},
             operation("free", "Free", acts_on_concept_keys=["memory"])], "s2",
        ),
    ]
    merged = merge_canonicalization_payloads(batches, warnings=[])
    assert len(merged["concepts"]) == 2
    assert len(merged["operations"]) == 2
    assert merged["concepts"][0]["related_concept_keys"] == ["memory"]
    assert merged["concepts"][0]["key_operation_keys"] == ["run", "free"]
    assert merged["operations"][0]["acts_on_concept_keys"] == ["runtime", "memory"]


def test_matching_names_and_definitions_are_not_enough_without_reused_keys():
    notices: list[str] = []
    merged = merge_canonicalization_payloads([
        payload([concept("first", "Runtime")], [operation("first_op", "Run")], "s1"),
        payload([concept("second", "Runtime")], [operation("second_op", "Run")], "s2"),
    ], warnings=notices)
    assert len(merged["concepts"]) == len(merged["operations"]) == 2
    assert merged["stage_bindings"]["s2"] == {
        "concept_keys": ["second"], "operation_keys": ["second_op"],
    }
    assert any("matching name alone" in notice for notice in notices)


@pytest.mark.parametrize("kind", ["concepts", "operations"])
@pytest.mark.parametrize("same_name", [True, False])
def test_colliding_keys_within_one_batch_fail_clearly(kind: str, same_name: bool):
    factory = concept if kind == "concepts" else operation
    answer = {"concepts": [], "operations": [], "stage_bindings": {}}
    answer[kind] = [factory("A-B", "First"), factory("a_b", "First" if same_name else "Second")]
    with pytest.raises(HarnessError) as error:
        merge_canonicalization_payloads([answer])
    assert error.value.code == "HARNESS_CANONICAL_KEY_COLLISION"
    assert "batch 1" in error.value.message
    assert "unique key" in error.value.message


@pytest.mark.parametrize("kind", ["concepts", "operations"])
def test_same_key_and_name_with_conflicting_definitions_stay_separate(kind: str):
    factory = concept if kind == "concepts" else operation
    batches = [{"concepts": [], "operations": [], "stage_bindings": {}} for _ in range(2)]
    batches[0][kind] = [factory("state", "State", definition="A persisted record")]
    batches[1][kind] = [factory("state", "State", definition="Transient execution state")]
    notices: list[str] = []
    result = merge_canonicalization_payloads(batches, warnings=notices)
    assert [item["key"] for item in result[kind]] == ["state", "state_2"]
    assert any("definition differs" in notice for notice in notices)


def test_prefix_and_substring_names_never_trigger_semantic_merges():
    batches = [
        payload([concept("agent", "Agent")], [operation("run", "Run")], "s1"),
        payload([concept("executor", "Agent Executor")],
                [operation("run_agent", "Run Agent")], "s2"),
    ]
    merged = merge_canonicalization_payloads(batches, warnings=[])
    assert len(merged["concepts"]) == len(merged["operations"]) == 2
    assert merged["stage_bindings"]["s2"] == {
        "concept_keys": ["executor"], "operation_keys": ["run_agent"],
    }


@pytest.mark.parametrize("owner,field", [
    ("concepts", "related_concept_keys"), ("concepts", "key_operation_keys"),
    ("operations", "acts_on_concept_keys"), ("stage_bindings", "concept_keys"),
    ("stage_bindings", "operation_keys"),
])
def test_unresolved_refs_fail_instead_of_being_silently_lost(owner: str, field: str):
    answer = payload([concept("c", "Concept")], [operation("o", "Operation")], "s1")
    target = answer[owner]["s1"] if owner == "stage_bindings" else answer[owner][0]
    target[field] = ["unknown"]
    with pytest.raises(HarnessError) as error:
        merge_canonicalization_payloads([answer])
    assert error.value.code == "HARNESS_INVALID_CANONICAL_REFERENCE"
    assert "unknown" in error.value.message
    assert "no unrelated fallback" in error.value.message


def test_duplicate_display_names_must_be_referenced_by_key():
    answer = payload([concept("a", "State"), concept("b", "State")], [], "s")
    answer["stage_bindings"]["s"]["concept_keys"] = ["State"]
    with pytest.raises(HarnessError, match="ambiguous"):
        merge_canonicalization_payloads([answer], warnings=[])
    answer["stage_bindings"]["s"]["concept_keys"] = ["a", "b"]
    assert merge_canonicalization_payloads([answer], warnings=[])["stage_bindings"]["s"] == {
        "concept_keys": ["a", "b"], "operation_keys": [],
    }


@pytest.mark.parametrize("value", ["", None, 3])
def test_empty_and_non_string_refs_cannot_accidentally_resolve(value: Any):
    answer = payload([concept("entity_0", "Fallback")], [], "s")
    answer["stage_bindings"]["s"]["concept_keys"] = [value]
    with pytest.raises(HarnessError) as error:
        merge_canonicalization_payloads([answer])
    assert error.value.code == "HARNESS_INVALID_CANONICAL_REFERENCE"


class RecordingServices:
    def __init__(self, answers: list[dict[str, Any]]) -> None:
        self.answers = answers
        self.calls: list[dict[str, Any]] = []

    def is_cancelled(self) -> bool:
        return False

    async def complete_structured(self, **request: Any) -> dict[str, Any]:
        self.calls.append(request)
        return self.answers[len(self.calls) - 1]


def context(count: int) -> HarnessContext:
    return HarnessContext(
        run_id="r", project_id="p", settings={"language": "en"},
        stage_drafts=[{
            "key": f"s{index}", "title": f"Stage {index}", "local_goal": "g",
            "local_outcome": "o", "concept_candidates": [f"Concept {index}"],
            "operation_candidates": [f"Operation {index}"],
            "implementation_details": [{"title": "Teaching", "action": "full body " * 200}],
        } for index in range(count)],
    )


def answer_for(keys: list[str]) -> dict[str, Any]:
    return {
        "concepts": [concept("runtime", "Runtime")],
        "operations": [operation("run", "Run")],
        "stage_bindings": {
            key: {"concept_keys": ["runtime"], "operation_keys": ["run"]} for key in keys
        },
    }


@pytest.mark.asyncio
async def test_next_batch_sees_registry_and_whole_run_names_without_extra_calls():
    ctx = context(CANONICALIZE_BATCH_SIZE + 1)
    before = deepcopy(ctx.stage_drafts)
    first = answer_for([f"s{i}" for i in range(CANONICALIZE_BATCH_SIZE)])
    second = answer_for([f"s{CANONICALIZE_BATCH_SIZE}"])
    second["concepts"] = []
    second["operations"] = []  # Accepted keys may be referenced without repeating the body.
    services = RecordingServices([first, second])
    result = await CanonicalizeStep().execute(ctx, services)
    assert len(services.calls) == 2
    assert len(result.checkpoint_patch["concepts"]) == 1
    assert len(result.checkpoint_patch["operations"]) == 1
    assert f'"Concept {CANONICALIZE_BATCH_SIZE}"' in services.calls[0]["user_prompt"]
    assert '"key":"runtime","name":"Runtime","definition":"Definition of Runtime"' in (
        services.calls[1]["user_prompt"]
    )
    assert '"key":"run","name":"Run","definition":"Definition of Run"' in (
        services.calls[1]["user_prompt"]
    )
    assert all(len(decode_payload(call["user_prompt"])["stages"]) <= CANONICALIZE_BATCH_SIZE
               for call in services.calls)
    assert ctx.stage_drafts == before, "the registry projection must not truncate teaching bodies"


@pytest.mark.asyncio
async def test_same_name_entities_are_not_merged_by_the_final_h60_pass():
    ctx = context(CANONICALIZE_BATCH_SIZE + 1)
    first = answer_for([f"s{i}" for i in range(CANONICALIZE_BATCH_SIZE)])
    second = payload([concept("vm", "Runtime", definition="Virtual machine")],
                     [operation("vm_run", "Run", definition="Start VM")],
                     f"s{CANONICALIZE_BATCH_SIZE}")
    result = await CanonicalizeStep().execute(ctx, RecordingServices([first, second]))
    assert [item["key"] for item in result.checkpoint_patch["concepts"]] == ["runtime", "vm"]
    assert [item["key"] for item in result.checkpoint_patch["operations"]] == ["run", "vm_run"]
    assert any("matching name alone" in warning for warning in result.warnings)


@pytest.mark.asyncio
@pytest.mark.parametrize("fault", ["missing", "empty_concepts", "empty_operations", "unknown"])
async def test_invalid_stage_binding_fails_without_unrelated_first_entity(fault: str):
    ctx = context(1)
    answer = answer_for(["s0"])
    if fault == "missing":
        answer["stage_bindings"] = {}
    elif fault == "unknown":
        answer["stage_bindings"]["s0"]["concept_keys"] = ["missing"]
    else:
        field = "concept_keys" if fault == "empty_concepts" else "operation_keys"
        answer["stage_bindings"]["s0"][field] = []
    services = RecordingServices([answer])
    with pytest.raises(HarnessError) as error:
        await CanonicalizeStep().execute(ctx, services)
    assert error.value.code in {
        "HARNESS_INVALID_STAGE_BINDING", "HARNESS_INVALID_CANONICAL_REFERENCE",
    }
    assert "s0" in error.value.message
    assert len(services.calls) == 1
    assert ctx.stage_bindings == {}


@pytest.mark.asyncio
async def test_candidate_limit_fails_before_calls_without_silent_truncation():
    ctx = context(1)
    ctx.stage_drafts[0]["concept_candidates"] = [f"C{i}" for i in range(MAX_CONCEPT_CANDIDATES + 1)]
    services = RecordingServices([])
    with pytest.raises(HarnessError) as error:
        await CanonicalizeStep().execute(ctx, services)
    assert error.value.code == "HARNESS_CANONICAL_INPUT_LIMIT"
    assert services.calls == []
    assert len(ctx.stage_drafts[0]["concept_candidates"]) == MAX_CONCEPT_CANDIDATES + 1


@pytest.mark.asyncio
async def test_oversized_projection_fails_instead_of_truncating_teaching_content():
    ctx = context(1)
    ctx.stage_drafts[0]["local_goal"] = "g" * MAX_CANONICALIZE_PROMPT_CHARS
    before = deepcopy(ctx.stage_drafts)
    services = RecordingServices([])
    with pytest.raises(HarnessError) as error:
        await CanonicalizeStep().execute(ctx, services)
    assert error.value.code == "HARNESS_CANONICAL_INPUT_LIMIT"
    assert services.calls == []
    assert ctx.stage_drafts == before


@pytest.mark.asyncio
async def test_bad_second_batch_cannot_bind_to_an_unrelated_accepted_concept():
    ctx = context(CANONICALIZE_BATCH_SIZE + 1)
    first = answer_for([f"s{i}" for i in range(CANONICALIZE_BATCH_SIZE)])
    second = answer_for([f"s{CANONICALIZE_BATCH_SIZE}"])
    second["stage_bindings"][f"s{CANONICALIZE_BATCH_SIZE}"]["concept_keys"] = ["unresolved"]
    services = RecordingServices([first, second])
    with pytest.raises(HarnessError) as error:
        await CanonicalizeStep().execute(ctx, services)
    assert error.value.code == "HARNESS_INVALID_CANONICAL_REFERENCE"
    assert "batch 2" in error.value.message
    assert len(services.calls) == 2
    assert ctx.stage_bindings == {}


@pytest.mark.asyncio
async def test_registry_has_short_definitions_without_truncating_final_content():
    ctx = context(CANONICALIZE_BATCH_SIZE + 1)
    first = answer_for([f"s{i}" for i in range(CANONICALIZE_BATCH_SIZE)])
    definition = "x" * (REGISTRY_DEFINITION_LENGTH + 100)
    first["concepts"][0]["definition"] = definition
    second = answer_for([f"s{CANONICALIZE_BATCH_SIZE}"])
    second["concepts"] = []
    second["operations"] = []
    services = RecordingServices([first, second])
    result = await CanonicalizeStep().execute(ctx, services)
    assert '"definition":"' + "x" * REGISTRY_DEFINITION_LENGTH + '"' in (
        services.calls[1]["user_prompt"]
    )
    assert definition not in services.calls[1]["user_prompt"]
    assert result.checkpoint_patch["concepts"][0]["definition"] == definition
