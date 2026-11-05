"""Offline planning/continuity contracts, not claims of instructional efficacy."""

import copy
import json
from typing import Any

import pytest
from jsonschema import Draft202012Validator, ValidationError

from app.core.errors import HarnessError
from app.harness.context import HarnessContext
from app.harness.prompts import (
    build_canonicalize_prompt,
    build_critic_prompt,
    build_learning_layer_prompt,
    build_process_prompt,
    build_refine_prompt,
    build_stage_prompt,
    decode_payload,
)
from app.harness.schemas import PROCESSES_SCHEMA
from app.harness.steps.h40_processes import ProcessBuildStep, normalize_process
from app.harness.steps.h50_stages import (
    MAX_STAGES_PER_ENRICH_CALL,
    StageEnrichmentStep,
    normalize_stage,
)
from app.harness.steps.h80_learning import LearningLayerStep
from app.harness.steps.h90_assemble import Assembler

GOAL = {"key": "explain", "title": "Compare explanations", "outcome": "A justified conclusion"}


def raw_process(count: int = 4) -> dict[str, Any]:
    stages = [
        {
            "key": f"draft_{i}",
            "title": f"Compare explanation {i}",
            "local_outcome": f"An evidence-based comparison {i}",
        }
        for i in range(count)
    ]
    return {
        "key": "draft_process",
        "title": "Compare explanations",
        "outcome": GOAL["outcome"],
        "stages": stages,
        "teaching_plan": {
            "central_question": "What can these observations actually tell us?",
            "why_this_order": (
                "Observe before explaining; challenge an explanation before using it."
            ),
            "running_case": {
                "scenario": "A hypothetical garden with two wilting plants",
                "facts": ["Hypothetical case input: one plant has wet soil, the other dry soil."],
                "hypotheses": ["Lack of water could explain one plant, but not necessarily both."],
            },
            "stages": [
                {
                    "stage_key": stage["key"],
                    "learning_question": f"Which explanation survives comparison {i}?",
                    "why_now": f"Comparison {i} needs the previous evidence, not a copied label.",
                    "builds_on": [stages[i - 1]["key"]] if i else [],
                    "reasoning_moves": [
                        "Separate observations from explanations.",
                        "Compare an alternative explanation.",
                    ],
                    "check_focus": "Explain which observation could disconfirm the inference.",
                    "next_gap": "What does this comparison leave unexplained?",
                }
                for i, stage in enumerate(stages)
            ],
        },
    }


class RecordingServices:
    def __init__(self, process_payload: dict[str, Any] | None = None):
        self.process_payload = process_payload
        self.calls: list[dict[str, Any]] = []

    def is_cancelled(self) -> bool:
        return False

    async def complete_structured(self, **request: Any) -> dict[str, Any]:
        self.calls.append(copy.deepcopy(request))
        if request["schema"]["title"] == PROCESSES_SCHEMA["title"]:
            assert self.process_payload is not None
            return copy.deepcopy(self.process_payload)
        payload = decode_payload(request["user_prompt"])
        return {
            "stages": [
                {
                    "key": stage["key"],
                    "local_goal": "Compare the two explanations",
                    "why_it_exists": (
                        "Wet soil challenges the lack-of-water explanation, not all causes."
                    ),
                    "local_outcome": stage["local_outcome"],
                    "concept_candidates": ["Observation", "Inference"],
                    "operation_candidates": ["Compare explanations"],
                    "implementation_detail_candidates": [
                        {
                            "title": "Challenge the inference",
                            "action": "Compare the two plants and explain an alternative cause.",
                            "expected_result": (
                                "Wet soil limits the claim; a new observation is needed."
                            ),
                            "caution": (
                                "A label is not an explanation; consider another cause of wilting."
                            ),
                        }
                    ],
                    "example_candidate": {
                        "summary": "The hypothetical wet-soil plant is also wilted.",
                        "input": "Given wet soil and wilted leaves",
                        "output": "Lack of water alone does not explain both plants.",
                        "note": "This does not establish a cause; next compare other observations.",
                    },
                }
                for stage in payload["stages"]
            ]
        }


def context(process: dict[str, Any] | None = None) -> HarnessContext:
    return HarnessContext(
        run_id="offline",
        project_id="offline",
        settings={"language": "en"},
        goals=[copy.deepcopy(GOAL)],
        scope_result={"domain": "Reasoning from observations"},
        research_brief={"constraints": ["Do not infer causes from correlation alone."]},
        process_drafts=[process] if process else [],
    )


def test_new_h40_schema_requires_a_plan_but_legacy_normalization_does_not_invent_one():
    raw = raw_process()
    Draft202012Validator(PROCESSES_SCHEMA).validate(raw)
    del raw["teaching_plan"]
    with pytest.raises(ValidationError):
        Draft202012Validator(PROCESSES_SCHEMA).validate(raw)
    process = normalize_process(raw, GOAL)
    assert process["teaching_plan"] is None
    assert process["teaching_plan_status"] == "legacy_absent_unverified"


def test_normalization_rekeys_every_reference_preserves_prose_and_roundtrips_checkpoint():
    raw = raw_process()
    before = copy.deepcopy(raw)
    process = normalize_process(raw, GOAL)
    expected = copy.deepcopy(raw["teaching_plan"])
    for i, entry in enumerate(expected["stages"], start=1):
        entry["stage_key"] = f"explain_s{i}"
        entry["builds_on"] = [f"explain_s{i - 1}"] if i > 1 else []
    assert process["teaching_plan"] == expected
    assert process["teaching_plan_status"] == "present_unverified"
    assert raw == before
    ctx = context(process)
    resumed = HarnessContext.from_dict(json.loads(ctx.to_json()))
    assert resumed.process_drafts[0] == process
    # Re-normalizing an already canonical route must not corrupt its references.
    assert normalize_process(process, GOAL) == process


@pytest.mark.parametrize("ref", ["unknown", "draft_3", "draft_1"])
def test_unknown_forward_and_self_dependencies_are_errors(ref):
    raw = raw_process()
    raw["teaching_plan"]["stages"][1]["builds_on"] = [ref]
    with pytest.raises(HarnessError) as error:
        normalize_process(raw, GOAL)
    assert error.value.code in {
        "HARNESS_TEACHING_PLAN_REFERENCE",
        "HARNESS_TEACHING_PLAN_FORWARD_REFERENCE",
    }


@pytest.mark.parametrize("kind", ["missing", "duplicate", "out_of_order", "extra"])
def test_plan_must_cover_exactly_the_route_in_order(kind):
    raw = raw_process()
    entries = raw["teaching_plan"]["stages"]
    if kind == "missing":
        entries.pop()
    elif kind == "duplicate":
        entries[1] = copy.deepcopy(entries[0])
    elif kind == "out_of_order":
        entries[0], entries[1] = entries[1], entries[0]
    else:
        entries.append({**entries[-1], "stage_key": "not_in_route"})
    with pytest.raises(HarnessError):
        normalize_process(raw, GOAL)


@pytest.mark.parametrize("plan", [{}, "a paragraph", {"central_question": ""}])
def test_malformed_supplied_plans_cannot_silently_become_legacy(plan):
    raw = raw_process()
    raw["teaching_plan"] = plan
    with pytest.raises(HarnessError) as error:
        normalize_process(raw, GOAL)
    assert error.value.code == "HARNESS_TEACHING_PLAN_INVALID"


def test_planned_route_cannot_be_silently_truncated_by_depth_limit():
    raw = raw_process(6)
    with pytest.raises(HarnessError) as error:
        normalize_process(raw, GOAL, max_stages=5)
    assert error.value.code == "HARNESS_TEACHING_PLAN_TRUNCATED"
    del raw["teaching_plan"]
    legacy = normalize_process(raw, GOAL, max_stages=5)
    assert len(legacy["stages"]) == 5
    assert legacy["teaching_plan"] is None


@pytest.mark.parametrize("kind", ["duplicate_key", "empty_key", "lost_title"])
def test_plan_references_are_not_ambiguously_rewritten_or_lost(kind):
    raw = raw_process()
    if kind == "duplicate_key":
        raw["stages"][1]["key"] = raw["stages"][0]["key"]
    elif kind == "empty_key":
        raw["stages"][1]["key"] = ""
    else:
        raw["stages"][1]["title"] = " "
    with pytest.raises(HarnessError):
        normalize_process(raw, GOAL)


@pytest.mark.asyncio
async def test_h40_uses_the_existing_call_and_checkpoints_the_canonical_plan():
    ctx = context()
    ctx.settings.update({"generation_depth": "fast", "learner_level": "advanced"})
    services = RecordingServices(raw_process())
    result = await ProcessBuildStep().execute(ctx, services)
    assert len(services.calls) == 1
    request = services.calls[0]
    assert request["schema"] == PROCESSES_SCHEMA
    payload = decode_payload(request["user_prompt"])
    assert payload["max_stages"] == 5
    assert payload["learner_level"] == "advanced"
    assert payload["brief"] == ctx.research_brief
    ctx.apply(result.checkpoint_patch)
    assert ctx.process_drafts[0]["teaching_plan"]["stages"][0]["stage_key"] == "explain_s1"


@pytest.mark.asyncio
async def test_h50_batches_share_the_exact_plan_and_receive_precise_prior_context():
    process = normalize_process(raw_process(7), GOAL)
    ctx = context(process)
    before = ctx.to_dict()
    services = RecordingServices()
    result = await StageEnrichmentStep().execute(ctx, services)
    assert len(services.calls) == 3  # only the existing H50 batches, no planning call
    assert ctx.to_dict() == before
    for i, request in enumerate(services.calls):
        payload = decode_payload(request["user_prompt"])
        start = i * MAX_STAGES_PER_ENRICH_CALL
        expected_batch = process["stages"][start : start + MAX_STAGES_PER_ENRICH_CALL]
        assert payload["teaching_plan"] == process["teaching_plan"]
        assert payload["process"]["teaching_plan"] == process["teaching_plan"]
        assert payload["teaching_context"]["teaching_plan"] == process["teaching_plan"]
        assert payload["current_batch_stage_keys"] == [s["key"] for s in expected_batch]
        assert (
            payload["current_batch_plan"]
            == process["teaching_plan"]["stages"][start : start + MAX_STAGES_PER_ENRICH_CALL]
        )
        assert payload["prior_planned_outputs"] == [
            {"stage_key": s["key"], "planned_outcome": s["local_outcome"]}
            for s in process["stages"][:start]
        ]
        assert [s["key"] for s in payload["prior_stage_context"]] == [
            s["key"] for s in process["stages"][:start]
        ]
        if start:
            assert "challenges" in payload["prior_stage_context"][0]["why_it_exists"]
            assert payload["prior_stage_context"][0]["example"]["note"]
    assert result.checkpoint_patch["process_drafts"][0] == process
    assert len(result.checkpoint_patch["stage_drafts"]) == 7
    for stage in result.checkpoint_patch["stage_drafts"]:
        # The teaching survives in existing COP fields, not hidden extras H90 drops.
        assert "challenges" in stage["why_it_exists"]
        assert stage["example"]["note"]
        assert stage["implementation_details"][0]["expected_result"]
        assert "teaching_plan" not in stage


@pytest.mark.asyncio
async def test_legacy_h40_and_old_h50_checkpoints_are_explicitly_not_verified():
    raw = raw_process()
    del raw["teaching_plan"]
    h40 = await ProcessBuildStep().execute(context(), RecordingServices(raw))
    assert any("not verified" in warning for warning in h40.warnings)
    process = h40.checkpoint_patch["process_drafts"][0]
    # Simulate a checkpoint saved before metadata existed.
    del process["teaching_plan"]
    del process["teaching_plan_status"]
    services = RecordingServices()
    h50 = await StageEnrichmentStep().execute(context(process), services)
    assert any("not verified" in warning for warning in h50.warnings)
    checkpoint = h50.checkpoint_patch["process_drafts"][0]
    assert checkpoint["teaching_plan"] is None
    assert checkpoint["teaching_plan_status"] == "legacy_absent_unverified"
    for request in services.calls:
        payload = decode_payload(request["user_prompt"])
        assert payload["teaching_plan"] is None
        assert payload["current_batch_plan"] == []
        assert payload["teaching_plan_status"] == "legacy_absent_unverified"


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["missing", "duplicate", "extra"])
async def test_h50_cannot_fill_missing_planned_stages_with_generic_fallbacks(kind):
    class IncompleteServices(RecordingServices):
        async def complete_structured(self, **request):
            result = await super().complete_structured(**request)
            if kind == "missing":
                result["stages"].pop()
            elif kind == "duplicate":
                result["stages"][1] = result["stages"][0]
            else:
                result["stages"].append({"key": "not_current_batch"})
            return result

    services = IncompleteServices()
    with pytest.raises(HarnessError) as error:
        await StageEnrichmentStep().execute(
            context(normalize_process(raw_process(), GOAL)),
            services,
        )
    assert error.value.code == "HARNESS_TEACHING_PLAN_COVERAGE"
    assert len(services.calls) == 1


@pytest.mark.asyncio
async def test_invalid_checkpoint_plan_fails_before_an_enrichment_call():
    process = normalize_process(raw_process(), GOAL)
    process["teaching_plan"]["stages"][0]["builds_on"] = [process["stages"][-1]["key"]]
    services = RecordingServices()
    with pytest.raises(HarnessError):
        await StageEnrichmentStep().execute(context(process), services)
    assert services.calls == []


def test_teaching_content_is_lossless_and_candidates_are_not_cut_to_a_fixed_quota():
    body = "A necessary explanatory paragraph. " * 1000 + "Final limitation and recovery."
    raw = {
        "why_it_exists": body,
        "concept_candidates": [f"Concept {i}" for i in range(20)],
        "operation_candidates": [f"Operation {i}" for i in range(12)],
        "implementation_detail_candidates": [
            {"title": f"Reason {i}", "action": body} for i in range(12)
        ],
        "example_candidate": {"summary": body, "note": body},
    }
    source = {"key": "s", "title": "Compare", "local_outcome": "A conclusion", "process_key": "p"}
    normalized = normalize_stage(raw, source, "g", detail_density="compact")
    assert normalized["why_it_exists"] == body
    assert normalized["example"] == raw["example_candidate"]
    assert normalized["implementation_details"] == raw["implementation_detail_candidates"]
    assert normalized["concept_candidates"] == raw["concept_candidates"]
    assert normalized["operation_candidates"] == raw["operation_candidates"]


def test_prompts_require_semantic_reasoning_not_a_count_or_tooling_ritual():
    process = normalize_process(raw_process(), GOAL)
    h40, _ = build_process_prompt(goal=GOAL, scope={}, brief={}, siblings=[], language="en")
    h50, _ = build_stage_prompt(process=process, stages=process["stages"][:3], language="en")
    critic, _ = build_critic_prompt(artifact={}, language="en")
    refine, _ = build_refine_prompt(artifact={}, issues=[], locked_paths=[], language="en")
    assert "why_this_order" in h40 and "hypotheses" in h40
    assert "No fixed concept count" in h40
    assert "why each candidate Concept is needed" in h50
    assert "observation" in h50 and "inference" in h50 and "limits" in h50
    assert "transition" in h50 and "next_gap" in h50
    assert "shell/grep" in h50 and "non-code" in h50
    assert "not reality" in h50
    assert "actual misconceptions and logical jumps" in critic
    assert "quote the faulty claim" in critic
    assert "discriminating counterexample" in critic
    assert "not an unseen teaching" in critic
    assert "For a non-code task" in refine and "never insert shell/grep" in refine
    # H60 remains callable with its established signature; no call-order change.
    _, user = build_canonicalize_prompt(stages=[], language="en")
    assert decode_payload(user)["stages"] == []


@pytest.mark.asyncio
async def test_h80_receives_the_plan_and_assembly_preserves_public_teaching_verbatim():
    class LearningServices(RecordingServices):
        async def complete_structured(self, **request):
            if request["schema"]["title"] != "H80LearningLayer":
                return await super().complete_structured(**request)
            self.calls.append(copy.deepcopy(request))
            payload = decode_payload(request["user_prompt"])
            process = payload["processes"][0]
            plan = process["teaching_plan"]
            return {
                "mental_model": {
                    "summary": plan["central_question"] + " " + plan["why_this_order"],
                    "flow": [entry["why_now"] for entry in plan["stages"]],
                },
                "practices": [
                    {
                        "key": "practice",
                        "process_key": process["key"],
                        "title": "Compare explanations in the same garden",
                        "instructions": [
                            plan["running_case"]["scenario"],
                            *plan["stages"][0]["reasoning_moves"],
                        ],
                        "expected_outcome": (
                            "A justified inference with stated limits, not a cause claim."
                        ),
                        "checkpoint_questions": [plan["stages"][0]["check_focus"]],
                    }
                ],
                "expansion_map": [],
            }

    process = normalize_process(raw_process(), GOAL)
    ctx = context(process)
    services = LearningServices()
    ctx.apply((await StageEnrichmentStep().execute(ctx, services)).checkpoint_patch)
    ctx.apply((await LearningLayerStep().execute(ctx, services)).checkpoint_patch)
    h80_request = services.calls[-1]
    assert h80_request["schema"]["title"] == "H80LearningLayer"
    assert (
        decode_payload(h80_request["user_prompt"])["processes"][0]["teaching_plan"]
        == (process["teaching_plan"])
    )
    system = h80_request["system_prompt"]
    assert "why_this_order" in system
    assert "mental_model.summary" in system and "mental_model.flow" in system
    assert "remaining unknowns" in system and "Do not invent unrelated exercises" in system
    assert "checkpoint_questions" in system and "reasoning_moves" in system
    artifact = Assembler(ctx).assemble()
    assert artifact["mental_model"] == ctx.mental_model
    assert process["teaching_plan"]["why_this_order"] in artifact["mental_model"]["summary"]
    assert artifact["practices"][0]["instructions"] == ctx.practices[0]["instructions"]
    for source, assembled in zip(ctx.stage_drafts, artifact["stages"], strict=True):
        assert assembled["why_it_exists"] == source["why_it_exists"]
        assert assembled["example"] == source["example"]
        assert assembled["implementation_details"] == source["implementation_details"]
        assert "teaching_plan" not in assembled
    assert "teaching_plan" not in artifact["main_processes"][0]


def test_h80_keeps_public_order_rationale_when_practices_are_disabled():
    process = normalize_process(raw_process(), GOAL)
    system, user = build_learning_layer_prompt(
        scope={},
        processes=[process],
        practices_enabled=False,
        language="en",
    )
    assert "Do not generate any Practice" in system
    assert "Retain the order rationale even when Practices are disabled" in system
    assert decode_payload(user)["processes"][0]["teaching_plan"] == process["teaching_plan"]
