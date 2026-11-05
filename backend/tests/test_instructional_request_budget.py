"""Input repetition must not pay for a second copy of the same teaching text."""

from app.harness.prompts import build_canonicalize_prompt, build_stage_prompt, decode_payload


def test_canonicalization_sends_each_projected_stage_once():
    stages = [{"key": "s", "why_it_exists": "unique_reasoning_marker", "concept_candidates": []}]
    _, user = build_canonicalize_prompt(stages=stages, language="en")
    assert decode_payload(user)["stages"] == stages
    assert user.count("unique_reasoning_marker") == 1


def test_source_context_is_not_repeated_in_pretty_and_machine_payloads():
    context = {"source_material": [{"id": "source", "excerpt": "unique_source_marker"}]}
    _, user = build_stage_prompt(
        process={"key": "p", "stages": []},
        stages=[],
        language="en",
        teaching_context=context,
    )
    assert decode_payload(user)["teaching_context"] == context
    assert user.count("unique_source_marker") == 1
