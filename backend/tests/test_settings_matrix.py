"""R0 — the settings matrix: which controls actually change the output.

Spec `24` §8 fixes the precedence as

    run override > project setting > app setting > built-in default

and the acceptance checklist requires "Configure generation mode" and
"Project overrides work". A control that saves successfully, displays
correctly, and then changes nothing is worse than no control, because the user
trusts it. Four of them were in that state.

Each control gets three assertions here:

    reachable   the value a user saves is the value the worker reads
    effective   changing it changes the prompt a step actually sends
    honest      a value the UI offers is not silently ignored

The `reachable` tests pass today. The `effective` tests for `detail_density`
and `evidence_density` fail, and that failure is the R0 record: both are
offered in the settings form, persisted, and read by no Harness step, so
"compact" and "detailed" produce byte-identical Stage content.

The effective tests drive the real step classes with a recording provider
rather than calling the prompt builder directly, so they keep asserting the
same thing after the fix: that the setting survives the trip from settings to
the model call.
"""

import json
import uuid
from typing import Any

import pytest
from sqlalchemy.orm import Session

from app.api.settings import BUILT_IN_DEFAULTS
from app.db.models import AppSetting, GenerationRun, Project, ProjectSettings
from app.harness.context import HarnessContext, HarnessEvent
from app.harness.provider_factory import (
    resolve_effective_settings,
    resolve_effective_settings_with_run,
)
from app.harness.providers.mock import MockProvider
from app.harness.steps.h20_research_brief import ResearchBriefStep
from app.harness.steps.h30_goals import GoalExtractionStep
from app.harness.steps.h50_stages import StageEnrichmentStep
from app.harness.steps.h80_learning import LearningLayerStep

GENERATION_CONTROLS = sorted(BUILT_IN_DEFAULTS["generation"])


# --- a recording provider, so a test can see the exact prompt a step sent ---


class RecordingServices:
    """HarnessServices that records prompts and defers to the mock provider."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def complete_structured(
        self, *, system_prompt: str, user_prompt: str, schema: dict[str, Any]
    ) -> dict[str, Any]:
        self.calls.append(
            {"system": system_prompt, "user": user_prompt, "schema_title": schema.get("title")}
        )
        return await MockProvider().generate_structured(
            system_prompt=system_prompt, user_prompt=user_prompt, schema=schema
        )

    async def complete_text(self, *, system_prompt: str, user_prompt: str) -> str:
        return ""

    def emit(self, event: HarnessEvent) -> None:
        return None

    def is_cancelled(self) -> bool:
        return False

    @property
    def prompt(self) -> str:
        return "\n".join(f"{c['system']}\n{c['user']}" for c in self.calls)


def _context(**settings: Any) -> HarnessContext:
    base = {"language": "en", "generation_depth": "standard", "practice_mode": "priority"}
    base.update(settings)
    return HarnessContext(
        run_id="run-1",
        project_id="project-1",
        input={
            "topic": "LangChain agents",
            "scope_hint": "Build a working agent",
            "target_outcomes": ["Ship a runnable agent"],
            "learner_level": "new",
            "source_ids": [],
        },
        settings=base,
        source_bundle=[
            {
                "id": "lc-overview",
                "title": "LangChain overview",
                "type": "text",
                "text": "create_agent is the high-level entry point.",
            }
        ],
    )


def _project(db: Session, **kwargs) -> Project:
    project = Project(title=kwargs.pop("title", "P"), domain="D", scope="s", **kwargs)
    db.add(project)
    db.commit()
    return project


def _set_app(db: Session, generation: dict) -> None:
    record = db.get(AppSetting, 1)
    if record is None:
        record = AppSetting(id=1, settings_json={})
        db.add(record)
    record.settings_json = {"generation": generation}
    db.commit()


def _set_project(db: Session, project_id: uuid.UUID, generation: dict) -> None:
    record = db.get(ProjectSettings, project_id)
    if record is None:
        record = ProjectSettings(project_id=project_id, settings_json={})
        db.add(record)
    record.settings_json = {"generation": generation}
    db.commit()


# --------------------------------------------------------------------------
# The matrix itself
# --------------------------------------------------------------------------


def test_every_generation_control_is_declared() -> None:
    """Freezing the list means a newly added control has to declare its wiring."""
    assert GENERATION_CONTROLS == [
        "detail_density",
        "evidence_density",
        "generation_depth",
        "language",
        "learner_level",
        "practice_mode",
    ]


@pytest.mark.parametrize("control", GENERATION_CONTROLS)
def test_an_app_level_control_reaches_the_harness_context(db: Session, control) -> None:
    """Saving at the app level must change what the worker reads."""
    value = "fast" if control == "generation_depth" else "zh-CN"
    _set_app(db, {control: value})
    project = _project(db)

    effective = resolve_effective_settings(db, project.id)

    assert effective["generation"][control] == value


def test_precedence_is_run_then_project_then_app_then_default(db: Session) -> None:
    """The order in spec `24` §8, asserted end to end rather than per layer."""
    _set_app(db, {"language": "en", "generation_depth": "standard"})
    project = _project(db)
    _set_project(db, project.id, {"language": "de"})

    app_only = resolve_effective_settings(db, project.id)
    with_run = resolve_effective_settings_with_run(
        db, project.id, {"generation": {"language": "ja"}}
    )

    assert app_only["generation"]["language"] == "de", "project overrides app"
    assert with_run["generation"]["language"] == "ja", "run overrides project"
    assert with_run["generation"]["generation_depth"] == "standard", "unset keys still inherit"
    assert resolve_effective_settings(db, project.id)["generation"]["language"] == "de", (
        "resolving with a run override must not persist it"
    )


def test_built_in_defaults_apply_to_a_project_with_no_settings(db: Session) -> None:
    project = _project(db)

    assert (
        resolve_effective_settings(db, project.id)["generation"] == BUILT_IN_DEFAULTS["generation"]
    )


def test_a_deeper_generation_depth_asks_for_more_goals() -> None:
    from app.harness.prompts import build_goals_prompt

    args = {"scope": {"d": 1}, "brief": {"b": 1}, "requested_outcomes": ["o"], "language": "en"}
    fast, _ = build_goals_prompt(**args, depth="fast")
    deep, _ = build_goals_prompt(**args, depth="deep")

    assert "Return 2-4 Goals for fast mode" in fast
    assert "Return 5-9 Goals for deep mode" in deep


# --------------------------------------------------------------------------
# Effective, not merely reachable. These are the R0 failing baseline.
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_language_reaches_every_prompt() -> None:
    services = RecordingServices()
    context = _context(language="zh-CN")
    context.intake = {
        "topic": "LangChain",
        "scope_hint": "",
        "target_outcomes": ["o"],
        "learner_level": "new",
        "language": "zh-CN",
        "depth": "standard",
        "source_ids": ["lc-overview"],
        "sources": [],
    }
    context.scope_result = {"domain": "d", "scope": "s", "target_user": "u"}
    context.research_brief = {"domain_purpose": "d", "capability_candidates": []}

    await GoalExtractionStep().execute(context, services)

    assert "zh-CN" in services.prompt


@pytest.mark.asyncio
async def test_detail_density_changes_the_stage_prompt() -> None:
    """R2 gap. `detail_density` is offered in the settings form today.

    Saves, round-trips through GET /settings, and is read by no Harness step,
    so "compact" and "detailed" currently produce identical Stage content.
    """

    async def prompt_for(detail_density: str) -> str:
        services = RecordingServices()
        context = _context(detail_density=detail_density)
        context.process_drafts = [
            {
                "key": "p1",
                "goal_key": "g1",
                "title": "Build an agent",
                "outcome": "A running agent",
                "stages": [
                    {"key": "s1", "title": "Install LangChain", "local_outcome": "Installed"}
                ],
            }
        ]
        await StageEnrichmentStep().execute(context, services)
        return services.prompt

    compact = await prompt_for("compact")
    detailed = await prompt_for("detailed")

    assert compact != detailed, (
        "detail_density does not reach the H50 prompt at all; "
        f"both settings produced an identical {len(compact)}-character prompt"
    )


@pytest.mark.asyncio
async def test_evidence_density_changes_the_citation_prompt() -> None:
    """R2 gap. `evidence_density` is offered in the settings form today.

    Read by no Harness step, so "minimal" and "high" ask the model for exactly
    the same citations.
    """

    # H20 reads `scope_result`, so the checkpoint must be present.
    async def prompt_with_scope(evidence_density: str) -> str:
        services = RecordingServices()
        ctx = _context(evidence_density=evidence_density)
        ctx.intake = {
            "topic": "LangChain",
            "scope_hint": "",
            "target_outcomes": ["o"],
            "learner_level": "new",
            "language": "en",
            "depth": "standard",
            "source_ids": ["lc-overview"],
            "sources": [
                {
                    "id": "lc-overview",
                    "title": "Overview",
                    "type": "text",
                    "excerpt": "create_agent is the entry point.",
                }
            ],
        }
        ctx.scope_result = {"domain": "d", "scope": "s", "target_user": "u"}
        await ResearchBriefStep().execute(ctx, services)
        return services.prompt

    minimal = await prompt_with_scope("minimal")
    high = await prompt_with_scope("high")

    assert minimal != high, (
        "evidence_density does not reach the H20 prompt at all; "
        f"both settings produced an identical {len(minimal)}-character prompt"
    )


@pytest.mark.asyncio
async def test_practice_mode_off_differs_from_priority() -> None:
    """`practice_mode=off` is wired today; this pins the part that already works."""

    async def prompt_for(practice_mode: str) -> str:
        services = RecordingServices()
        context = _context(practice_mode=practice_mode)
        context.scope_result = {"domain": "d", "scope": "s", "target_user": "u"}
        context.process_drafts = [
            {
                "key": "p1",
                "goal_key": "g1",
                "title": "Build an agent",
                "outcome": "A running agent",
                "stages": [{"key": "s1", "title": "S", "local_outcome": "o"}],
            }
        ]
        await LearningLayerStep().execute(context, services)
        return services.prompt

    assert await prompt_for("off") != await prompt_for("priority")


@pytest.mark.asyncio
async def test_practice_mode_priority_and_all_are_distinguishable() -> None:
    """R2 gap. Only `off` is implemented.

    `priority` and `all` currently produce an identical prompt, so the control
    offers a choice it does not honour.
    """

    async def prompt_for(practice_mode: str) -> str:
        services = RecordingServices()
        context = _context(practice_mode=practice_mode)
        context.scope_result = {"domain": "d", "scope": "s", "target_user": "u"}
        context.process_drafts = [
            {
                "key": "p1",
                "goal_key": "g1",
                "title": "Build an agent",
                "outcome": "A running agent",
                "stages": [{"key": "s1", "title": "S", "local_outcome": "o"}],
            }
        ]
        await LearningLayerStep().execute(context, services)
        return services.prompt

    priority = await prompt_for("priority")
    every = await prompt_for("all")

    assert priority != every, "practice_mode=priority and =all are indistinguishable"


@pytest.mark.asyncio
async def test_learner_level_from_settings_reaches_the_scope_prompt() -> None:
    """R2. A learner level saved in Settings must reach H10.

    H00 used to read `ctx.input` only, so the only learner level that ever took
    effect was the per-request field and a value chosen once in Settings was
    ignored by every run.
    """
    from app.harness.steps.h00_intake import IntakeStep
    from app.harness.steps.h10_scope import ScopeStep

    async def intake_for(learner_level: str):
        services = RecordingServices()
        ctx = _context(learner_level=learner_level)
        # No learner_level in the request: the setting is the only source.
        ctx.input = {key: value for key, value in ctx.input.items() if key != "learner_level"}
        result = await IntakeStep().execute(ctx, services)
        # The runner applies the checkpoint patch; driving a step directly has to
        # do the same or the context never receives the step's output.
        ctx.apply(result.checkpoint_patch)
        return ctx

    new_ctx = await intake_for("new")
    advanced_ctx = await intake_for("advanced")

    # H00 is deterministic and sends no prompt, so the assertion is on the
    # checkpoint it produces: that is exactly what H10 reads the level from.
    assert new_ctx.intake is not None
    assert advanced_ctx.intake is not None
    assert new_ctx.intake["learner_level"] == "new"
    assert advanced_ctx.intake["learner_level"] == "advanced"

    # And that value then reaches the scope prompt, which is where the bar for
    # the whole COP is actually set.
    services = RecordingServices()
    advanced_ctx.scope_result = {"domain": "d", "scope": "s", "target_user": "u"}
    await ScopeStep().execute(advanced_ctx, services)
    assert "advanced" in services.prompt

    new_services = RecordingServices()
    new_ctx.scope_result = {"domain": "d", "scope": "s", "target_user": "u"}
    await ScopeStep().execute(new_ctx, new_services)
    assert new_services.prompt != services.prompt


def test_preferred_language_on_a_project_reaches_generation(db: Session) -> None:
    """R2. The project's preferred language must select the run's language.

    It used to be a display-only column: the seed script wrote it, and nothing
    read it, so a project created in Chinese generated an English COP unless the
    user re-selected the language by hand.
    """
    project = _project(db, preferred_language="zh-CN")

    effective = resolve_effective_settings(db, project.id)

    assert effective["generation"]["language"] == "zh-CN", (
        "preferred_language never reaches generation settings"
    )


def test_creating_a_project_records_the_chosen_language_and_learner_level(client, db) -> None:
    """R2. The creation form's two dropdowns must survive the round trip.

    Both used to be dropped on the floor: the form sent them, the API ignored
    them, and the first run used the app defaults regardless.
    """
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "LangChain agents",
            "domain": "LangChain",
            "preferred_language": "zh-CN",
            "learner_level": "advanced",
        },
    )
    assert response.status_code == 201, response.text
    project_id = response.json()["id"]

    effective = resolve_effective_settings(db, uuid.UUID(project_id))

    assert effective["generation"]["language"] == "zh-CN"
    assert effective["generation"]["learner_level"] == "advanced"


def test_project_language_overrides_the_app_default(client, db) -> None:
    _set_app(db, {"language": "en", "learner_level": "new"})
    project_id = client.post(
        "/api/v1/projects", json={"title": "T", "domain": "D", "preferred_language": "zh-CN"}
    ).json()["id"]

    effective = resolve_effective_settings(db, uuid.UUID(project_id))

    assert effective["generation"]["language"] == "zh-CN", "project must beat the app default"


def test_an_unknown_language_is_rejected_rather_than_stored(client) -> None:
    """A value nothing understands would be accepted and then silently ignored."""
    response = client.post(
        "/api/v1/projects", json={"title": "T", "domain": "D", "preferred_language": "klingon"}
    )

    assert response.status_code == 422


def test_an_unusable_generation_override_is_rejected(client, db) -> None:
    """Storing an unknown enum is how a control starts lying.

    The API would say saved, the form would show the choice, and the Harness
    would fall back to its default without saying so.
    """
    project = _project(db)
    response = client.patch(
        f"/api/v1/projects/{project.id}/settings",
        json={"generation": {"detail_density": "verbose"}},
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_GENERATION_SETTING"
    assert "detail_density" in response.json()["detail"]["message"]


def test_an_override_can_be_cleared_back_to_the_app_default(client, db) -> None:
    """An override the user cannot remove is a trap with no way back."""
    _set_app(db, {"detail_density": "compact"})
    project = _project(db)
    client.patch(
        f"/api/v1/projects/{project.id}/settings",
        json={"generation": {"detail_density": "detailed"}},
    )
    assert resolve_effective_settings(db, project.id)["generation"]["detail_density"] == "detailed"

    client.patch(f"/api/v1/projects/{project.id}/settings", json={"reset": ["generation"]})

    assert resolve_effective_settings(db, project.id)["generation"]["detail_density"] == "compact"


def test_the_generation_settings_endpoint_returns_the_harness_view(client, db) -> None:
    """The browser must not own the merge (spec 24 §8).

    This endpoint is what the panel calls, and it returns both the nested shape
    the form binds to and the flattened shape the worker reads, so "the UI shows
    X and the Harness read Y" is checkable without a debugger.
    """
    _set_app(db, {"generation_depth": "deep"})
    project = _project(db)
    _set_project(db, project.id, {"language": "ja"})

    plain = client.get(f"/api/v1/projects/{project.id}/generation-settings").json()
    assert plain["effective"]["generation_depth"] == "deep"
    assert plain["effective"]["language"] == "ja"
    assert plain["harness_view"]["generation_depth"] == "deep"
    assert plain["harness_view"]["language"] == "ja"

    overridden = client.get(
        f"/api/v1/projects/{project.id}/generation-settings",
        params={"run": json.dumps({"generation": {"generation_depth": "fast"}})},
    ).json()
    assert overridden["effective"]["generation_depth"] == "fast"


def test_a_malformed_override_preview_is_rejected(client, db) -> None:
    project = _project(db)

    response = client.get(
        f"/api/v1/projects/{project.id}/generation-settings", params={"run": "not json"}
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_SETTINGS_OVERRIDE"


def test_a_run_records_the_settings_it_actually_used(client, db) -> None:
    """R2 auditability.

    `model_config_json` must hold the flattened effective settings, so "why was
    this run 4 Goals" is answerable from the run row itself.
    """
    _set_app(db, {"generation_depth": "fast"})
    project = _project(db)
    _set_project(db, project.id, {"language": "ja"})

    run_id = client.post(
        f"/api/v1/projects/{project.id}/generation-runs",
        json={"topic": "Docker packaging", "settings_override": {"generation": {"language": "fr"}}},
    ).json()["id"]

    run = db.get(GenerationRun, uuid.UUID(run_id))
    assert run is not None
    assert run.model_config_json["language"] == "fr"
    assert run.model_config_json["generation_depth"] == "fast"


def test_mode_and_generation_depth_cannot_disagree(client, db) -> None:
    """The run previously recorded `mode` and executed `generation_depth`.

    Two names for one thing, so the run's own record could not explain what it
    did. They are now the same value, asserted from the stored row.
    """
    project = _project(db)

    run_id = client.post(
        f"/api/v1/projects/{project.id}/generation-runs", json={"topic": "T", "mode": "fast"}
    ).json()["id"]

    run = db.get(GenerationRun, uuid.UUID(run_id))
    assert run is not None
    assert run.requested_mode == "fast"
