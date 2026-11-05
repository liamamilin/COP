"""Pure prompt regressions: no database, provider calls, or saved-data writes."""

from app.harness.prompts import (
    build_critic_prompt,
    build_goals_prompt,
    build_process_prompt,
    build_refine_prompt,
    build_scope_prompt,
    build_stage_prompt,
    decode_payload,
)
from app.harness.reader_contract import (
    CRITIC_GUIDANCE,
    GOAL_GUIDANCE,
    PROCESS_GUIDANCE,
    SCOPE_GUIDANCE,
    STAGE_GUIDANCE,
)


def test_scope_explains_result_approach_and_unconfirmed_assumptions():
    system, user = build_scope_prompt(
        topic="A personal tool",
        scope_hint="",
        target_outcomes=[],
        learner_level="new",
        language="zh-CN",
        sources=[],
    )
    assert SCOPE_GUIDANCE in system
    assert "not a paragraph" in system
    assert "do not present the assumption as confirmed" in system
    assert decode_payload(user)["topic"] == "A personal tool"


def test_goals_do_not_turn_every_request_into_project_documentation():
    system, user = build_goals_prompt(
        scope={},
        brief={},
        requested_outcomes=[],
        depth="standard",
        language="auto",
    )
    assert GOAL_GUIDANCE in system
    assert "planning document is a legitimate result" in system
    assert "when the user requested planning" in system
    assert decode_payload(user)["requested_outcomes"] == []


def test_process_keeps_one_continuous_default_route_without_repeated_ceremony():
    goal = {"key": "tool", "title": "Build a tool"}
    system, user = build_process_prompt(
        goal=goal,
        scope={},
        brief={},
        siblings=[],
        language="auto",
    )
    assert PROCESS_GUIDANCE in system
    assert "one default route" in system
    assert decode_payload(user)["goal"] == goal


def test_enrichment_and_refinement_share_action_check_and_honesty_guidance():
    stages = [{"key": "run", "title": "Run a task"}]
    stage_system, user = build_stage_prompt(process={}, stages=stages, language="auto")
    refine_system, _ = build_refine_prompt(
        artifact={},
        issues=[],
        locked_paths=["stages/run/title"],
        language="auto",
    )
    assert STAGE_GUIDANCE in stage_system
    assert STAGE_GUIDANCE in refine_system
    assert "Do not force shell commands" in stage_system
    assert "Examples are hypothetical" in stage_system
    assert "never rewrite a locked" in refine_system
    assert decode_payload(user)["stages"] == stages


def test_critic_reviews_semantic_usefulness_without_new_codes_or_schema_fields():
    artifact = {"schema_version": "0.1", "stages": []}
    system, user = build_critic_prompt(artifact=artifact, language="auto")
    assert CRITIC_GUIDANCE in system
    assert "not merely field presence" in system
    assert "PROCESS_MAINLINE_HIDDEN" in system
    assert decode_payload(user)["artifact"] == artifact
