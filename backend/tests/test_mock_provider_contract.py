"""The Mock Provider must honour the same contract as a real provider.

Spec `19` requires the mock to make the acceptance path real, and spec `15` §9
requires the acceptance path to run without live credentials. That only holds if
the mock's output satisfies the same constraints a real provider's does -- a mock
that quietly produces something a real one never would makes the whole suite
green and the product broken.

Every test here drives `MockProvider` through the same prompt builders the
Harness uses, rather than calling its private helpers, so the assertion is about
the response shape the rest of the pipeline will actually receive.
"""

import json
import re
from typing import Any

import pytest

from app.harness.prompts import build_refine_prompt
from app.harness.providers.mock import MockProvider
from app.harness.steps.h140_refine_target import targeted_artifact_view

PAYLOAD = re.compile(r"<payload>(.*?)</payload>", re.S)

#: Ids are namespaced by type, the way the assembler names them, so the tests
#: exercise the real id shape rather than a convenient one.
GOAL_ID = "goal.ship_a_capability"


def payload_of(user_prompt: str) -> dict[str, Any]:
    match = PAYLOAD.search(user_prompt)
    assert match, "the prompt must carry a machine-readable payload block"
    return json.loads(match.group(1))


def artifact(goal_id: str = "goal.ship_a_capability") -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "artifact_id": "a",
        "domain": {"name": "D", "scope": "s", "non_goals": []},
        "goals": [
            {
                "id": goal_id,
                "title": "T",
                "outcome": "O",
                "why_it_matters": "Without it the workflow cannot be trusted.",
            }
        ],
        "main_processes": [],
        "stages": [],
        "concepts": [],
        "operations": [],
        "branches": [],
        "practices": [],
        "expansion_map": [],
        "metadata": {},
    }


async def ask_refine(view: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, Any]:
    system, user = build_refine_prompt(artifact=view, issues=issues, locked_paths=[], language="en")
    return await MockProvider().generate_structured(
        system_prompt=system,
        user_prompt=user,
        schema={
            "title": "H110Refine",
            "type": "object",
            "properties": {
                "revisions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "entity_type": {"type": "string"},
                            "entity_key": {"type": "string"},
                            "field": {"type": "string"},
                            "value": {"type": "string"},
                        },
                        "required": ["entity_type", "entity_key", "field", "value"],
                    },
                }
            },
            "required": ["revisions"],
        },
    )


@pytest.mark.asyncio
async def test_a_targeted_refinement_proposes_something_without_an_instruction() -> None:
    """The bug this pins: an empty diff with no explanation.

    H140 sends a deliberately scoped view -- the one entity the run may touch --
    rather than the whole artifact. The mock's deterministic fallback used to
    search that view for a full collection, found nothing, and returned no
    revisions at all. The user saw a review screen with an empty diff and no
    reason, which reads as a broken feature rather than as "nothing to change".
    """
    view = targeted_artifact_view(artifact(), "goal", GOAL_ID)

    response = await ask_refine(
        view,
        [
            {
                "code": "USER_REQUESTED_REFINEMENT",
                "entity_ref": GOAL_ID,
                "explanation": "The user asked for this entity to be improved.",
                "recommended_change": "",  # the user typed nothing
            }
        ],
    )

    assert response["revisions"], "a targeted refinement with no issue must still propose a change"
    revision = response["revisions"][0]
    assert revision["entity_type"] == "goal"
    assert revision["entity_key"] == GOAL_ID, "the key must be the entity id, not a split fragment"
    assert revision["field"] == "why_it_matters"
    assert revision["value"].strip(), "a proposed change may not be blank"


@pytest.mark.asyncio
async def test_a_targeted_refinement_still_prefers_the_users_instruction() -> None:
    """The instruction is the user's own words and outranks the synthesis."""
    view = targeted_artifact_view(artifact(), "goal", GOAL_ID)

    response = await ask_refine(
        view,
        [
            {
                "code": "USER_REQUESTED_REFINEMENT",
                "entity_ref": GOAL_ID,
                "explanation": "x",
                "recommended_change": "Make the outcome measurable.",
            }
        ],
    )

    assert response["revisions"][0]["value"] == "Make the outcome measurable."


@pytest.mark.asyncio
async def test_a_full_artifact_prompt_still_finds_the_entity() -> None:
    """The other payload shape must keep working, not just the targeted one."""
    response = await ask_refine(
        artifact(),
        [
            {
                "code": "GOAL_TOO_VAGUE",
                "entity_ref": GOAL_ID,
                "explanation": "x",
                "recommended_change": "Name the capability result.",
            }
        ],
    )

    assert response["revisions"][0]["entity_key"] == GOAL_ID


@pytest.mark.asyncio
async def test_a_locked_entity_is_never_proposed() -> None:
    """The mock must not propose a change the user made by hand."""
    view = targeted_artifact_view(artifact(), "goal", GOAL_ID)
    system, user = build_refine_prompt(
        artifact=view,
        issues=[
            {
                "code": "USER_REQUESTED_REFINEMENT",
                "entity_ref": GOAL_ID,
                "explanation": "x",
                "recommended_change": "Something new.",
            }
        ],
        locked_paths=[GOAL_ID],
        language="en",
    )

    response = await MockProvider().generate_structured(
        system_prompt=system,
        user_prompt=user,
        schema={"title": "H110Refine", "type": "object", "properties": {}, "required": []},
    )

    assert response["revisions"] == []


def test_the_payload_block_is_still_machine_readable() -> None:
    """Guards the assumption both prompt shapes above depend on."""
    view = targeted_artifact_view(artifact(), "goal", GOAL_ID)
    _, user = build_refine_prompt(artifact=view, issues=[], locked_paths=[], language="en")

    decoded = payload_of(user)

    assert decoded["artifact"]["target"]["entity_id"] == GOAL_ID
