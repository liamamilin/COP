"""End-to-end Harness pipeline tests against the deterministic mock provider.

These cover the M4 acceptance path: `topic -> run -> streamed progress ->
validated candidate COP`, plus the failure modes the milestone requires
(malformed output, timeout, rate limit, cancellation, resume after restart).
"""

import json
from typing import Any

import pytest

from app.domain.cop_models import COPArtifact
from app.harness.context import HarnessContext, HarnessEvent, StepResult, StepStatus
from app.harness.providers.base import ProviderError
from app.harness.providers.mock import MockProvider
from app.harness.runner import _final_status, build_metrics, run_pipeline
from app.harness.steps import PHASES, STEP_LABELS, STEP_PIPELINE
from app.harness.steps.h30_goals import GoalExtractionStep
from app.harness.steps.h60_canonicalize import canonicalization_input, canonicalize
from app.harness.steps.h70_compression import detect_shared_foundation
from app.harness.steps.h110_refine import apply_revisions
from app.harness.steps.h120_validate import ValidateRepairStep, resolve_schema_path, validate
from app.harness.steps.h130_finalize import FinalizeStep


class FakeStore:
    """In-memory RunStore that records what the runner persisted."""

    def __init__(self) -> None:
        self.events: list[HarnessEvent] = []
        self.checkpoints: list[HarnessContext] = []
        self.heartbeats = 0
        self.cancelled = False
        self.candidate: dict[str, Any] | None = None

    def emit(self, run_id: str, events: list[HarnessEvent]) -> None:
        self.events.extend(events)

    def save_checkpoint(self, run_id: str, context: HarnessContext) -> None:
        self.checkpoints.append(HarnessContext.from_dict(json.loads(context.to_json())))

    def heartbeat(self, run_id: str) -> None:
        self.heartbeats += 1

    def metrics(self, run_id: str) -> dict[str, Any]:
        return {}

    def is_cancelled(self, run_id: str) -> bool:
        return self.cancelled

    def set_candidate(self, run_id: str, artifact: dict[str, Any] | None) -> None:
        self.candidate = artifact

    def types(self) -> list[str]:
        return [event.event_type for event in self.events]

    def steps_started(self) -> list[str]:
        return [
            str(event.payload.get("step"))
            for event in self.events
            if event.event_type == "step.started"
        ]


class _SilentServices:
    """HarnessServices for driving a single step outside the full pipeline."""

    def __init__(self, store: FakeStore) -> None:
        self._store = store
        self.calls: list[dict[str, Any]] = []

    async def complete_structured(
        self, *, system_prompt: str, user_prompt: str, schema: dict[str, Any]
    ) -> dict[str, Any]:
        return await MockProvider().generate_structured(
            system_prompt=system_prompt, user_prompt=user_prompt, schema=schema
        )

    async def complete_text(self, *, system_prompt: str, user_prompt: str) -> str:
        return ""

    def emit(self, event: HarnessEvent) -> None:
        self._store.emit("run", [event])

    def is_cancelled(self) -> bool:
        return False


class _SevenGoalServices(_SilentServices):
    async def complete_structured(
        self, *, system_prompt: str, user_prompt: str, schema: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "goals": [
                {"key": f"g{index}", "title": f"Goal {index}", "outcome": "Ship a result"}
                for index in range(1, 8)
            ]
        }


def make_context(**overrides: Any) -> HarnessContext:
    defaults: dict[str, Any] = {
        "run_id": "run-1",
        "project_id": "project-1",
        "input": {
            "topic": "Docker Application Packaging",
            "scope_hint": "Package and run a real service",
            "target_outcomes": ["Ship a containerized service"],
            "learner_level": "some_experience",
            "source_ids": [],
        },
        "settings": {"language": "en", "generation_depth": "standard", "practice_mode": "priority"},
    }
    defaults.update(overrides)
    return HarnessContext(**defaults)


@pytest.mark.asyncio
async def test_fast_mode_caps_model_goals_at_four() -> None:
    context = make_context(
        settings={"language": "en", "generation_depth": "fast"},
    )
    context.scope_result = {"domain": "d", "scope": "s", "target_user": "u"}
    context.research_brief = {"domain_purpose": "d"}

    result = await GoalExtractionStep().execute(context, _SevenGoalServices(FakeStore()))

    assert len(result.checkpoint_patch["goals"]) == 4
    assert any("first 4 of 7" in warning for warning in result.warnings)


def test_canonicalization_input_drops_large_stage_details() -> None:
    compact = canonicalization_input(
        [
            {
                "key": "s1",
                "title": "Deploy",
                "local_goal": "Run the service",
                "local_outcome": "Healthy service",
                "concept_candidates": [f"concept-{index}" for index in range(12)],
                "operation_candidates": [f"operation-{index}" for index in range(8)],
                "implementation_details": [{"large": "value"}],
                "example": {"large": "value"},
                "evidence_refs": [{"source_id": "source"}],
            }
        ]
    )

    assert set(compact[0]) == {
        "key",
        "title",
        "local_goal",
        "local_outcome",
        "concept_candidates",
        "operation_candidates",
    }
    assert len(compact[0]["concept_candidates"]) == 8
    assert len(compact[0]["operation_candidates"]) == 6


async def run(ctx: HarnessContext, provider: Any = None) -> tuple[str, HarnessContext, FakeStore]:
    store = FakeStore()
    outcome = await run_pipeline(ctx, provider or MockProvider(), store)
    return outcome.status, outcome.context, store


@pytest.mark.asyncio
async def test_full_pipeline_produces_a_valid_cop_artifact() -> None:
    status, context, store = await run(make_context())

    assert status == "completed", store.types()
    artifact = context.artifact
    assert artifact is not None

    # Schema and semantic validation both pass.
    assert validate(artifact, resolve_schema_path()) == []
    parsed = COPArtifact.model_validate(artifact)
    assert parsed.goals
    assert parsed.main_processes
    assert parsed.stages
    assert parsed.concepts
    assert parsed.operations
    assert parsed.practices

    # Every process reaches a Goal and keeps at least one Stage.
    goal_ids = {goal.id for goal in parsed.goals}
    stage_ids = {stage.id for stage in parsed.stages}
    for process in parsed.main_processes:
        assert process.goal_ref in goal_ids
        assert process.stage_refs
        assert set(process.stage_refs) <= stage_ids

    # Every Stage is operable: it has a local goal, a Concept, and an Operation.
    concept_ids = {concept.id for concept in parsed.concepts}
    operation_ids = {operation.id for operation in parsed.operations}
    for stage in parsed.stages:
        assert stage.local_goal
        assert set(stage.concept_refs) <= concept_ids
        assert set(stage.operation_refs) <= operation_ids


@pytest.mark.asyncio
async def test_pipeline_emits_progress_for_every_step_and_phase() -> None:
    _status, _context, store = await run(make_context())

    assert store.types()[0] == "run.started"
    assert store.types()[-1] != "step.started"
    assert "run.completed" not in store.types()  # emitted by the worker, not the runner
    assert store.steps_started() == [step.name for step in STEP_PIPELINE]

    # Progress is observable as user-facing phases, not internal step names.
    completed = {
        event.payload.get("step") for event in store.events if event.event_type == "step.completed"
    }
    phase_of = {step: key for key, _label, steps in PHASES for step in steps}
    assert {phase_of[step] for step in completed} == {key for key, _l, _s in PHASES}
    for step in STEP_PIPELINE:
        assert STEP_LABELS[step.name]


@pytest.mark.asyncio
async def test_pipeline_persists_a_checkpoint_after_each_step() -> None:
    _status, _context, store = await run(make_context())

    # One checkpoint per step, and every one survives serialization.
    assert len(store.checkpoints) == len(STEP_PIPELINE)
    assert store.heartbeats == len(STEP_PIPELINE)
    final = store.checkpoints[-1]
    assert final.completed_checkpoints() == [
        "scope",
        "research_brief",
        "goals",
        "processes",
        "stages",
        "cop_core",
        "compression",
        "learning_layer",
        "critic",
        "artifact",
    ]
    assert final.artifact is not None


@pytest.mark.asyncio
async def test_run_is_deterministic_across_identical_inputs() -> None:
    first, ctx_a, _ = await run(make_context())
    second, ctx_b, _ = await run(make_context())

    assert first == second == "completed"
    # artifact_id is a fresh uuid by design; everything else must match.
    a = {**ctx_a.artifact, "artifact_id": "x"}
    b = {**ctx_b.artifact, "artifact_id": "x"}
    assert a == b


@pytest.mark.asyncio
async def test_rate_limited_provider_fails_the_run_without_losing_checkpoints() -> None:
    status, context, store = await run(make_context(), MockProvider("rate_limit"))

    assert status == "failed"
    assert "run.failed" in store.types()
    assert store.checkpoints, "work before the failure must be checkpointed"
    # H00 is deterministic, so it completes before any provider call.
    assert context.intake is not None


@pytest.mark.asyncio
async def test_a_failed_run_reports_its_real_cause() -> None:
    """A generic 'generation failed' is not actionable.

    The user has to be told the provider rate-limited them, not that something
    opaque went wrong, or they cannot decide between waiting and switching
    models.
    """
    status, _context, store = await run(make_context(), MockProvider("rate_limit"))

    assert status == "failed"
    failure = next(event for event in store.events if event.event_type == "run.failed")
    assert failure.payload["code"] == "PROVIDER_RATE_LIMITED"
    assert "rate limited" in failure.payload["message"]
    assert failure.payload["step"] == "H10", "the failure must name the step that failed"


@pytest.mark.asyncio
async def test_stage_bindings_survive_canonicalization() -> None:
    """A Stage's Concept/Operation bindings must survive the H60 merge.

    Canonicalization renames entities, so a binding that only survives when the
    model repeats the exact key would silently collapse to a single fallback
    Concept and Operation per Stage, which reads as a broken main line.
    """
    _status, context, _store = await run(make_context())
    artifact = context.artifact
    binding_keys = set(context.stage_bindings)

    for stage in artifact["stages"]:
        assert stage["concept_refs"], f"{stage['id']} lost its Concept binding"
        assert stage["operation_refs"], f"{stage['id']} lost its Operation binding"
        # Bindings were resolved against canonical keys, not left dangling.
        assert set(stage["concept_refs"]) <= {c["id"] for c in artifact["concepts"]}
        assert set(stage["operation_refs"]) <= {o["id"] for o in artifact["operations"]}

    assert binding_keys == {stage["key"] for stage in context.stage_drafts}


def test_canonicalization_resolves_bindings_written_as_names_or_keys() -> None:
    """A binding may reference an entity by key or by display name."""
    result = canonicalize(
        {
            "concepts": [
                {"key": "Tool", "name": "Tool", "definition": "d", "role": "r"},
                {"key": "Schema", "name": "Schema", "definition": "d", "role": "r"},
            ],
            "operations": [
                {"key": "Define", "name": "Define", "definition": "d"},
            ],
            "stage_bindings": {
                "s1": {"concept_keys": ["Tool"], "operation_keys": ["define"]},
                "s2": {"concept_keys": ["Schema", "Tool"], "operation_keys": []},
                "s3": {"concept_keys": ["Missing"], "operation_keys": ["Define"]},
            },
        }
    )

    assert result["stage_bindings"]["s1"] == {
        "concept_keys": ["tool"],
        "operation_keys": ["define"],
    }
    # Order is preserved and both a key and a name resolve.
    assert result["stage_bindings"]["s2"]["concept_keys"] == ["schema", "tool"]
    # An unknown reference is dropped rather than creating a phantom entity.
    assert result["stage_bindings"]["s3"] == {"concept_keys": [], "operation_keys": ["define"]}


def test_canonicalization_merges_synonyms_instead_of_duplicating() -> None:
    result = canonicalize(
        {
            "concepts": [
                {"key": "agent", "name": "Agent", "definition": "first", "role": "r"},
                {"key": "agent_v2", "name": "agent", "definition": "second", "role": "r"},
                {"key": "tool", "name": "Tool", "definition": "", "role": "r"},
            ],
            "operations": [
                {"key": "bind", "name": "Bind", "definition": "d"},
                {"key": "bind2", "name": "bind", "definition": "d2"},
            ],
            "stage_bindings": {},
        }
    )

    assert [c["name"] for c in result["concepts"]] == ["Agent", "Tool"]
    assert [o["name"] for o in result["operations"]] == ["Bind"]


@pytest.mark.asyncio
async def test_assembly_is_structurally_sound_before_validation() -> None:
    """The assembler repairs the output of earlier steps, not the reverse.

    Steps normalize unbindable Concept/Operation references before assembly, so
    by H90 the artifact is already well-formed. Validation exists to catch
    structural bugs and hostile output, not to paper over step normalization.
    """
    _status, context, _store = await run(make_context())
    assert validate(context.artifact, resolve_schema_path()) == []


@pytest.mark.asyncio
async def test_structurally_broken_artifact_lands_in_needs_attention() -> None:
    """A candidate that cannot be repaired must not be reported as valid.

    Reproduces the real failure the tail steps exist for: an artifact with a
    broken reference reaches H120, the repair model cannot fix it, and the run
    must end in `needs_attention` with the user's work intact.
    """
    _status, ctx, _store = await run(make_context())
    assert validate(ctx.artifact, resolve_schema_path()) == []

    # Corrupt one reference, as a model-caused defect would.
    ctx.artifact["main_processes"][0]["stage_refs"] = ["stage.does_not_exist"]
    ctx.settings["max_repair_attempts"] = 1

    store = FakeStore()
    validate_step = ValidateRepairStep()
    finalize_step = FinalizeStep()

    repair = await validate_step.execute(ctx, _SilentServices(store))
    store.emit("run", repair.events)
    store.emit("run", [HarnessEvent("step.warning", {"warnings": repair.warnings})])

    assert repair.status is StepStatus.PARTIAL_SUCCESS
    assert any("still fails validation" in warning for warning in repair.warnings)

    final = await finalize_step.execute(ctx, _SilentServices(store))
    store.emit("run", final.events)
    assert final.status is StepStatus.PARTIAL_SUCCESS
    assert final.events[0].payload["valid"] is False

    # Upstream checkpoints are untouched, so the run is still worth retrying.
    assert ctx.scope_result is not None
    assert ctx.goals
    assert ctx.stage_drafts
    assert _final_status(ctx) == "needs_attention"


@pytest.mark.asyncio
async def test_cancellation_stops_before_the_next_step() -> None:
    store = FakeStore()
    ctx = make_context()
    outcome_holder: dict[str, Any] = {}

    async def execute() -> None:
        outcome = await run_pipeline(ctx, MockProvider(), store)
        outcome_holder["status"] = outcome.status

    # Flip the flag as soon as the first step reports progress.
    original_emit = store.emit

    def emit(run_id: str, events: list[HarnessEvent]) -> None:
        original_emit(run_id, events)
        if any(event.event_type == "step.completed" for event in events):
            store.cancelled = True

    store.emit = emit  # type: ignore[method-assign]
    await execute()

    assert outcome_holder["status"] == "cancelled"
    assert store.steps_started() == ["H00"]


@pytest.mark.asyncio
async def test_resume_skips_steps_already_checkpointed() -> None:
    _status, context, _store = await run(make_context())

    resumed = HarnessContext.from_dict(json.loads(context.to_json()))
    resumed.artifact = None
    resumed.critic_report = None
    store = FakeStore()

    outcome = await run_pipeline(resumed, MockProvider(), store)

    assert outcome.status == "completed"
    # Everything up to H90 was already checkpointed, so only the tail re-runs.
    assert store.steps_started() == ["H90", "H100", "H110", "H120", "H130"]
    assert "run.resumed" in store.types()


@pytest.mark.asyncio
async def test_metrics_report_structure_and_provider_usage() -> None:
    _status, context, store = await run(make_context())
    services_calls = [
        {"step": "H30GoalExtraction", "attempts": 1, "latency_ms": 2} for _ in range(1)
    ]
    metrics = build_metrics(context, services_calls, started=0.0)

    assert metrics["provider_calls"] == 1
    assert metrics["goals"] == len(context.artifact["goals"])
    assert metrics["stages"] == len(context.artifact["stages"])
    assert "scope" in metrics["checkpoints"]


# --- deterministic units -------------------------------------------------


def test_shared_foundation_needs_a_repeated_leading_sequence() -> None:
    processes = [
        {"key": "p1", "stage_keys": ["a1", "a2", "a3"]},
        {"key": "p2", "stage_keys": ["b1", "b2"]},
    ]
    foundation, starts, stage_map = detect_shared_foundation(processes)
    assert foundation is None
    assert all(value["type"] == "zero" for value in starts.values())
    assert stage_map["p1"] == ["a1", "a2", "a3"]


def test_shared_foundation_compresses_identical_leading_stages() -> None:
    processes = [
        {"key": "p1", "stage_keys": ["a1", "a2", "a3"]},
        {"key": "p2", "stage_keys": ["a1", "a2", "b1"]},
    ]
    foundation, starts, stage_map = detect_shared_foundation(processes)

    assert foundation is not None
    assert foundation["stage_keys"] == ["a1", "a2"]
    assert all(value["type"] == "foundation" for value in starts.values())
    assert stage_map["p1"] == ["a3"]
    assert stage_map["p2"] == ["b1"]


def test_shared_foundation_is_skipped_for_a_single_shared_stage() -> None:
    processes = [
        {"key": "p1", "stage_keys": ["a1", "a2"]},
        {"key": "p2", "stage_keys": ["a1", "b1"]},
    ]
    foundation, starts, _ = detect_shared_foundation(processes)

    # One leading stage is too small to hide; keeping it inline preserves the
    # traceability back to Zero State.
    assert foundation is None
    assert all(value["type"] == "zero" for value in starts.values())


def test_refiner_never_touches_locked_or_structural_fields() -> None:
    artifact = {
        "goals": [{"id": "goal.a", "title": "A", "outcome": "O", "why_it_matters": "W"}],
        "stages": [{"id": "stage.a", "title": "S", "local_goal": "L", "why_it_exists": "Y"}],
    }
    updated, applied, rejected = apply_revisions(
        artifact,
        [
            {
                "entity_type": "goal",
                "entity_key": "goal.a",
                "field": "why_it_matters",
                "value": "User-authored, must survive",
            },
            {
                "entity_type": "goal",
                "entity_key": "goal.a",
                "field": "title",
                "value": "Renamed",
            },
            {
                "entity_type": "stage",
                "entity_key": "stage.a",
                "field": "id",
                "value": "hijacked",
            },
            {"entity_type": "stage", "entity_key": "stage.missing", "field": "title", "value": "x"},
        ],
        ["goal.a.why_it_matters"],
    )

    assert applied == ["goal.goal.a.title"]
    assert updated["goals"][0]["why_it_matters"] == "W"
    assert updated["goals"][0]["title"] == "Renamed"
    assert updated["stages"][0]["id"] == "stage.a"
    reasons = {item["reason"] for item in rejected}
    assert "path is locked by user edits" in reasons
    assert "'id' is not refinable" in reasons
    assert "entity id not found in artifact" in reasons
    # The original artifact is never mutated in place.
    assert artifact["goals"][0]["title"] == "A"


def test_validation_reports_broken_references() -> None:
    ctx_artifact = {
        "schema_version": "0.1",
        "artifact_id": "a",
        "domain": {"name": "D", "scope": "s", "target_user": "u"},
        "mental_model": {"summary": "m"},
        "goals": [{"id": "goal.a", "title": "A", "outcome": "O"}],
        "shared_foundations": [],
        "main_processes": [
            {
                "id": "process.a",
                "goal_ref": "goal.a",
                "title": "P",
                "start": {"type": "zero"},
                "stage_refs": ["stage.missing"],
                "outcome": "done",
            }
        ],
        "stages": [],
        "concepts": [],
        "operations": [],
        "branches": [],
        "practices": [],
        "expansion_map": [],
        "metadata": {},
    }
    errors = validate(ctx_artifact, None)
    assert errors
    assert any("stage" in error for error in errors)


def test_step_result_helpers_carry_stable_codes() -> None:
    fatal = StepResult.fatal("HARNESS_X", "broken")
    assert fatal.status is StepStatus.FATAL_FAILURE
    assert fatal.events[0].payload["code"] == "HARNESS_X"

    retry = StepResult.retryable("PROVIDER_TIMEOUT", "slow")
    assert retry.status is StepStatus.RETRYABLE_FAILURE


def test_provider_error_is_classified_as_retryable() -> None:
    error = ProviderError("PROVIDER_RATE_LIMITED", "slow down", retryable=True)
    assert error.retryable is True
