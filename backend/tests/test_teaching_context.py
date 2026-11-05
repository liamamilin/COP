"""Teaching regressions with in-memory checkpoints and recording services only."""

import copy

import pytest

from app.harness.context import HarnessContext
from app.harness.prompts import build_stage_prompt, decode_payload
from app.harness.steps.h50_stages import StageEnrichmentStep, normalize_stage
from app.harness.steps.h60_canonicalize import canonicalization_input
from app.harness.teaching_context import teaching_context


def context():
    return HarnessContext(
        run_id="r",
        project_id="p",
        settings={"learner_level": "new"},
        scope_result={"domain": "A service", "target_user": "A beginner", "scope": "Local test"},
        goals=[
            {"key": "setup", "title": "Prepare", "outcome": "A local environment"},
            {
                "key": "run",
                "title": "Run",
                "outcome": "A running service",
                "prerequisite_goal_keys": ["setup"],
            },
        ],
        process_drafts=[
            {
                "key": "p1",
                "goal_key": "run",
                "title": "Run a service",
                "outcome": "A result",
                "stages": [{"key": "s1", "title": "Write config", "local_outcome": "Config"}],
            }
        ],
        source_bundle=[{"id": "source", "title": "Documentation", "excerpt": "Source text " * 300}],
    )


def test_context_carries_learner_scope_prior_outputs_and_source_excerpts_without_mutation():
    ctx = context()
    before = copy.deepcopy(ctx.to_dict())
    teaching = teaching_context(ctx, ctx.process_drafts[0])
    assert teaching["learner_level"] == "new"
    assert teaching["scope"]["target_user"] == "A beginner"
    assert teaching["prerequisite_planned_outputs"][0]["planned_outcome"] == "A local environment"
    assert teaching["source_material"][0]["id"] == "source"
    assert len(teaching["source_material"][0]["excerpt"]) == 1800
    assert teaching["source_material"][0]["excerpt_truncated"] is True
    assert ctx.to_dict() == before


def test_prompt_preserves_frozen_context_and_does_not_equate_density_with_omissions():
    ctx = context()
    teaching = teaching_context(ctx, ctx.process_drafts[0])
    system, user = build_stage_prompt(
        process=ctx.process_drafts[0],
        stages=[],
        language="auto",
        teaching_context=teaching,
    )
    assert decode_payload(user)["teaching_context"] == teaching
    assert "not a hard ceiling" in system
    assert "complete minimal configuration" in system
    assert "causal reasoning" in system


def test_normalization_never_silently_discards_a_method_tail_for_compact_density():
    details = [{"title": f"Action {i}", "action": f"Do {i}"} for i in range(8)]
    stage = normalize_stage(
        {"implementation_detail_candidates": details},
        {"key": "s", "title": "A task", "local_outcome": "Result", "process_key": "p"},
        "g",
        detail_density="compact",
    )
    assert stage["implementation_details"] == details


def test_concept_projection_keeps_causal_action_context_but_not_large_code_files():
    projected = canonicalization_input(
        [
            {
                "key": "s",
                "why_it_exists": "An action changes an object",
                "implementation_details": [
                    {"title": "Write", "action": "Create config", "command": "x" * 50000}
                ],
            }
        ]
    )[0]
    assert projected["why_it_exists"] == "An action changes an object"
    assert projected["action_context"][0]["action_excerpt"] == "Create config"
    assert "command" not in str(projected)


@pytest.mark.asyncio
async def test_enrichment_passes_learning_context_using_the_existing_call_and_reports_density():
    class RecordingServices:
        def __init__(self):
            self.calls = []

        def is_cancelled(self):
            return False

        async def complete_structured(self, **request):
            self.calls.append(request)
            return {
                "stages": [
                    {
                        "key": "s1",
                        "local_goal": "Write a config",
                        "local_outcome": "Config",
                        "implementation_detail_candidates": [
                            {"title": f"Action {i}", "action": f"Do {i}"} for i in range(8)
                        ],
                        "example_candidate": {"summary": "A worked example"},
                    }
                ]
            }

    ctx = context()
    services = RecordingServices()
    result = await StageEnrichmentStep().execute(ctx, services)
    assert len(services.calls) == 1  # no new model pass was introduced
    payload = decode_payload(services.calls[0]["user_prompt"])
    assert payload["teaching_context"]["goal"]["key"] == "run"
    assert len(result.checkpoint_patch["stage_drafts"][0]["implementation_details"]) == 8
    assert any("all were preserved" in warning for warning in result.warnings)
