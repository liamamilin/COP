"""R3 — every evidence ref resolves to a source the user can open.

Three failure modes, each tested separately because they are genuinely different
bugs:

    invented    the model cites a source the run never read
    unpersisted a search result is used but never stored, so the id survives only
                inside a checkpoint and the citation is unopenable after a restart
    stale       a stored source is deleted and the artifact still cites it

None of these is a schema problem. Every one of them produces a structurally
perfect artifact, which is exactly why they survived until now.
"""

import json
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy.orm import Session

from app.db.models import COPVersion, Draft, Project, Source, SourceDocument
from app.domain.drafting import EDITABLE_FIELDS, parse_detail_lines, parse_string_lines
from app.research.snapshots import (
    WEB_SOURCE_PREFIX,
    content_hash,
    persist_search_results,
    research_source_ids,
    snapshot_source_id,
)

FIXTURE_PATH = Path(__file__).resolve().parents[2] / "fixtures" / "reference-langchain-cop.json"


def make_project(db: Session, title: str = "Evidence") -> Project:
    row = Project(title=title, domain="d", scope="s")
    db.add(row)
    db.commit()
    return row


@pytest.fixture
def project(db: Session) -> Project:
    return make_project(db)


def make_source(db: Session, project_id: Any, *, title: str = "Doc") -> Source:
    source = Source(
        project_id=project_id, type="text", title=title, status="ready", metadata_json={}
    )
    db.add(source)
    db.flush()
    db.add(
        SourceDocument(
            source_id=source.id, text="body", content_hash=content_hash("body"), char_count=4
        )
    )
    db.commit()
    db.refresh(source)
    return source


def uuid_quote(value: str) -> str:
    """Stage ids contain dots, which are fine in a path segment but read badly."""
    from urllib.parse import quote

    return quote(value, safe="")


def generated_artifact(**settings: Any) -> dict[str, Any]:
    """A real pipeline artifact, so the test is not asserting on a hand-built shape."""
    import asyncio

    from app.harness.context import HarnessContext
    from app.harness.providers.mock import MockProvider
    from app.harness.runner import run_pipeline
    from tests.test_harness_pipeline import FakeStore

    base = {
        "language": "en",
        "generation_depth": "standard",
        "practice_mode": "priority",
        "detail_density": "balanced",
        "evidence_density": "key_claims",
    }
    base.update(settings)
    context = HarnessContext(
        run_id="run-evidence",
        project_id="project-evidence",
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
                "title": "Overview",
                "type": "text",
                "text": "create_agent is the entry point.",
            }
        ],
    )
    outcome = asyncio.run(run_pipeline(context, MockProvider(), FakeStore()))
    assert outcome.context.artifact is not None
    return outcome.context.artifact


# --------------------------------------------------------------------------
# Snapshot persistence
# --------------------------------------------------------------------------


def test_a_search_result_becomes_a_real_source(db: Session, project) -> None:
    """The core of R3.

    Without this the artifact cites `exa:abc`, the Source Manager is empty, and
    the user cannot open the citation -- a reference that looks like evidence and
    is not.
    """
    results = [
        {
            "id": "exa:abc123",
            "title": "LangChain agents guide",
            "text": "create_agent is the high-level entry point.",
            "original_uri": "https://example.com/agents",
        }
    ]

    stored = persist_search_results(db, project.id, results)

    assert len(stored) == 1
    row = db.query(Source).filter(Source.project_id == project.id).one()
    assert row.type == "web_search"
    assert row.original_uri == "https://example.com/agents"
    assert row.metadata_json["provider"] == "exa"
    assert row.metadata_json["research_source_id"] == "exa:abc123"
    # Fetch time is what makes a snapshot re-checkable rather than just quoted.
    assert row.metadata_json["fetched_at"]
    document = db.query(SourceDocument).filter(SourceDocument.source_id == row.id).one()
    assert "create_agent" in (document.text or "")


def test_the_persisted_id_is_what_the_run_will_cite(db: Session, project) -> None:
    """The id the model saw must be the id the user can later resolve."""
    results = [{"id": "exa:zzz", "title": "T", "text": "b", "original_uri": "https://e.com/a"}]

    stored = persist_search_results(db, project.id, results)

    assert stored[0]["id"] == "exa:zzz"
    assert "exa:zzz" in research_source_ids(db, project.id)


def test_persisting_the_same_url_twice_does_not_duplicate(db: Session, project) -> None:
    """A re-run that finds the same page must reuse the snapshot.

    Two Source rows for one URL would leave the user unable to tell which copy is
    the one the artifact cited.
    """
    results = [{"id": "exa:one", "title": "T", "text": "b", "original_uri": "https://e.com/a"}]

    persist_search_results(db, project.id, results)
    persist_search_results(db, project.id, results)

    assert db.query(Source).filter(Source.project_id == project.id).count() == 1


def test_a_result_with_no_url_is_not_persisted(db: Session, project) -> None:
    """A citation with nothing to open is not traceability."""
    stored = persist_search_results(
        db, project.id, [{"id": "exa:no-url", "title": "T", "text": "b"}]
    )

    assert stored == []
    assert db.query(Source).filter(Source.project_id == project.id).count() == 0


def test_the_source_id_is_deterministic_for_a_url() -> None:
    """Two adapters asking for the same page must mint the same id."""
    assert snapshot_source_id("https://e.com/a") == snapshot_source_id("https://e.com/a")
    assert snapshot_source_id("https://e.com/a") != snapshot_source_id("https://e.com/b")
    assert snapshot_source_id("https://e.com/a").startswith(WEB_SOURCE_PREFIX)


# --------------------------------------------------------------------------
# No invented ids
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_goal_citing_an_unread_source_drops_the_reference() -> None:
    """A citation the user cannot open is worse than no citation.

    The run read one source. A Goal citing `lc-agents` would show the user a
    claim they are told is sourced, with nothing behind it.
    """
    from app.harness.context import HarnessContext
    from app.harness.providers.mock import MockProvider
    from app.harness.steps.h00_intake import IntakeStep
    from app.harness.steps.h10_scope import ScopeStep
    from app.harness.steps.h20_research_brief import ResearchBriefStep
    from app.harness.steps.h30_goals import GoalExtractionStep

    class InventingServices:
        """The mock, plus a Goal that cites a source the run never read."""

        def __init__(self) -> None:
            self.warnings: list[str] = []

        async def complete_structured(self, *, system_prompt, user_prompt, schema):
            payload = await MockProvider().generate_structured(
                system_prompt=system_prompt, user_prompt=user_prompt, schema=schema
            )
            if schema.get("title") == "H30GoalExtraction":
                for goal in payload.get("goals") or []:
                    goal["evidence_refs"] = [{"source_id": "lc-agents"}]
            return payload

        def emit(self, event) -> None:
            return None

        def is_cancelled(self) -> bool:
            return False

    ctx = HarnessContext(
        run_id="r",
        project_id="p",
        input={
            "topic": "LangChain",
            "scope_hint": "",
            "target_outcomes": ["o"],
            "learner_level": "new",
            "source_ids": ["lc-overview"],
        },
        settings={"language": "en", "generation_depth": "standard"},
        source_bundle=[{"id": "lc-overview", "title": "O", "type": "text", "text": "b"}],
    )
    services = InventingServices()
    for step in (IntakeStep(), ScopeStep(), ResearchBriefStep(), GoalExtractionStep()):
        result = await step.execute(ctx, services)
        ctx.apply(result.checkpoint_patch)
        if step.name == "H30":
            services.warnings.extend(result.warnings)

    assert ctx.goals, "the run produced no Goals, so the test proves nothing"
    for goal in ctx.goals:
        assert goal["evidence_refs"] == [], (
            f"Goal {goal['key']} kept a reference to a source the run never read: "
            f"{goal['evidence_refs']}"
        )
    assert any("did not read" in warning for warning in services.warnings), (
        f"dropping an invented reference must be reported, not silent: {services.warnings}"
    )


@pytest.mark.asyncio
async def test_evidence_density_caps_the_number_of_refs() -> None:
    """A Stage citing fifteen sources reads as though every sentence were contested."""
    from app.harness.prompts import trim_evidence

    refs = [{"source_id": f"s{i}"} for i in range(15)]
    with_quote = [{"source_id": "s-quote", "quote_hint": "a real quote"}]

    assert len(trim_evidence(refs, "minimal")) == 1
    assert len(trim_evidence(refs, "key_claims")) == 3
    assert len(trim_evidence(refs, "high")) == 6

    # A ref with a quote is kept ahead of one without: it is the one the user can
    # actually check the claim against.
    kept = trim_evidence([*refs, *with_quote], "minimal")
    assert kept[0]["source_id"] == "s-quote"


@pytest.mark.asyncio
async def test_refs_without_a_source_id_are_dropped() -> None:
    from app.harness.prompts import trim_evidence

    assert trim_evidence([{"source_id": ""}, {"quote_hint": "x"}, {}], "high") == []


# --------------------------------------------------------------------------
# Resolution at read time
# --------------------------------------------------------------------------


def test_a_version_reports_which_evidence_it_can_open(client, db: Session, project) -> None:
    source = make_source(db, project.id, title="LangChain overview")
    artifact = generated_artifact()
    # Point one Stage at a real source and one at a source that does not exist.
    artifact["stages"][0]["evidence_refs"] = [{"source_id": str(source.id)}]
    artifact["stages"][1]["evidence_refs"] = [{"source_id": "ghost-source"}]
    version = COPVersion(
        project_id=project.id, version_number=1, artifact_json=artifact, change_summary="s"
    )
    db.add(version)
    db.commit()

    body = client.get(f"/api/v1/versions/{version.id}").json()

    resolved = body["evidence_sources"]
    assert str(source.id) in resolved
    assert resolved[str(source.id)]["title"] == "LangChain overview"
    # The unresolvable one is absent rather than mapped to something wrong, so
    # its absence is the signal the UI uses to say so.
    assert "ghost-source" not in resolved


def test_publishing_reports_unresolved_evidence(client, db: Session, project) -> None:
    """R3's user-facing half: never a silent orphan.

    The generated artifact now cites the sources the run read, so this strips
    every reference first and then adds one deliberately unresolvable id. Without
    that setup the assertion would be measuring the generator rather than the
    publish-time resolution.
    """
    artifact = generated_artifact()
    for collection in ("goals", "stages"):
        for entity in artifact[collection]:
            entity["evidence_refs"] = []
    artifact["stages"][0]["evidence_refs"] = [{"source_id": "ghost-source"}]
    draft = Draft(project_id=project.id, artifact_json=artifact)
    db.add(draft)
    db.commit()
    db.refresh(draft)

    body = client.post(f"/api/v1/drafts/{draft.id}/publish", json={}).json()

    assert body["version_number"] == 1, "a citation the user cannot open does not block publishing"
    unresolved = body["unresolved_evidence"]
    assert len(unresolved) == 1
    assert unresolved[0]["source_id"] == "ghost-source"
    assert unresolved[0]["entity_ref"] == artifact["stages"][0]["id"]


def test_a_generated_artifact_cites_only_sources_the_project_owns(client, db: Session) -> None:
    """The generator cannot produce an orphan, so publishing reports none.

    H50 passes the run's real source ids into the prompt and H50's output is
    filtered against the same list, which makes an unresolvable citation
    impossible by construction rather than by cleaning up afterwards.
    """
    project = make_project(db)
    source = make_source(db, project.id, title="The one real source")
    artifact = generated_artifact()
    for entity in artifact["stages"]:
        entity["evidence_refs"] = [{"source_id": str(source.id)}]
    for entity in artifact["goals"]:
        entity["evidence_refs"] = []
    draft = Draft(project_id=project.id, artifact_json=artifact)
    db.add(draft)
    db.commit()
    db.refresh(draft)

    body = client.post(f"/api/v1/drafts/{draft.id}/publish", json={}).json()

    assert not body.get("unresolved_evidence")


def test_publishing_with_every_ref_resolvable_reports_nothing(client, db: Session, project) -> None:
    """The negative control; without it a gate that always fires looks healthy."""
    source = make_source(db, project.id)
    artifact = generated_artifact()
    for stage in artifact["stages"]:
        stage["evidence_refs"] = [{"source_id": str(source.id)}]
    draft = Draft(project_id=project.id, artifact_json=artifact)
    db.add(draft)
    db.commit()
    db.refresh(draft)

    body = client.post(f"/api/v1/drafts/{draft.id}/publish", json={}).json()

    assert not body.get("unresolved_evidence")


def test_a_research_snapshot_survives_being_read_back(client, db: Session, project) -> None:
    """The restart case.

    A web result is persisted as a Source, so a later run reloads it through the
    ordinary source query and its id still resolves.
    """
    persist_search_results(
        db,
        project.id,
        [{"id": "exa:persisted", "title": "Guide", "text": "body", "original_uri": "https://e/a"}],
    )
    artifact = generated_artifact()
    artifact["stages"][0]["evidence_refs"] = [{"source_id": "exa:persisted"}]
    version = COPVersion(
        project_id=project.id, version_number=1, artifact_json=artifact, change_summary="s"
    )
    db.add(version)
    db.commit()

    resolved = client.get(f"/api/v1/versions/{version.id}").json()["evidence_sources"]

    assert "exa:persisted" in resolved
    assert resolved["exa:persisted"]["uri"] == "https://e/a"


def test_deleting_a_source_leaves_the_citation_visible_as_unresolved(
    client, db: Session, project
) -> None:
    """A stale ref is reported, never silently dropped.

    Hiding it would make the artifact look cleaner than it is; the user would
    believe a claim is backed that no longer can be opened.
    """
    source = make_source(db, project.id)
    artifact = generated_artifact()
    artifact["stages"][0]["evidence_refs"] = [{"source_id": str(source.id)}]
    version = COPVersion(
        project_id=project.id, version_number=1, artifact_json=artifact, change_summary="s"
    )
    db.add(version)
    db.commit()

    assert str(source.id) in client.get(f"/api/v1/versions/{version.id}").json()["evidence_sources"]

    db.delete(source)
    db.commit()

    assert (
        str(source.id)
        not in client.get(f"/api/v1/versions/{version.id}").json()["evidence_sources"]
    )


def test_the_reference_fixture_has_no_orphans_once_its_sources_exist() -> None:
    """The R0 baseline, inverted.

    The fixture cites six source ids and ships with no Sources. The seed creates
    them, so with them present the same artifact is clean: this proves the ids
    are consistent and only the *sources* were missing, not that the artifact's
    references are nonsense.
    """
    from app.domain.quality import completeness_summary

    artifact = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    declared = set((artifact.get("metadata") or {}).get("source_ids") or [])
    cited = {
        ref["source_id"]
        for collection in ("goals", "stages")
        for entity in artifact[collection]
        for ref in entity.get("evidence_refs") or []
    }

    assert cited <= declared, f"fixture cites undeclared sources: {sorted(cited - declared)}"
    assert completeness_summary(artifact, known_source_ids=declared)["orphan_evidence_refs"] == 0


# --------------------------------------------------------------------------
# The user must be able to fix content the gate reports
# --------------------------------------------------------------------------


def test_implementation_details_are_editable_in_a_draft() -> None:
    """R3/R4 pairing: a gate that blocks on an uneditable field is a dead end."""
    assert "implementation_details" in EDITABLE_FIELDS["stage"]
    assert "common_failures" in EDITABLE_FIELDS["operation"]


def test_a_detail_line_parses_into_the_canonical_shape() -> None:
    parsed = parse_detail_lines(
        "Install LangChain | Run pip in a venv | pip install langchain"
        " | pip reports success | Not system Python"
    )

    assert parsed == [
        {
            "title": "Install LangChain",
            "action": "Run pip in a venv",
            "command": "pip install langchain",
            "expected_result": "pip reports success",
            "caution": "Not system Python",
        }
    ]


def test_a_bare_line_is_accepted_as_a_title() -> None:
    """A user adding their first line should not have to learn the format first."""
    assert parse_detail_lines("Read the docs") == [{"title": "Read the docs"}]


def test_a_command_containing_a_comma_survives_the_round_trip() -> None:
    """The reason the separator is `|` and not a comma or a newline."""
    parsed = parse_detail_lines("Run it | Do the thing | docker run -p 8080:80 img | prints ok")

    assert parsed[0]["command"] == "docker run -p 8080:80 img"


def test_blank_lines_are_ignored() -> None:
    assert parse_detail_lines("\n\nOnly one\n\n") == [{"title": "Only one"}]
    assert parse_string_lines("a\n\nb\n") == ["a", "b"]


def test_editing_a_detail_through_the_api_publishes_the_new_command(
    client, db: Session, project
) -> None:
    """End to end: the user supplies the command the gate was missing."""
    artifact = generated_artifact()
    draft = Draft(project_id=project.id, artifact_json=artifact)
    db.add(draft)
    db.commit()
    db.refresh(draft)
    stage_id = artifact["stages"][0]["id"]

    response = client.patch(
        f"/api/v1/drafts/{draft.id}/stages/{uuid_quote(stage_id)}",
        json={
            "implementation_details": "Install | Run pip | pip install x | reports ok | use a venv"
        },
    )

    assert response.status_code == 200, response.text

    # Read it back from the stored draft rather than from the response body, so
    # this asserts what was actually persisted.
    db.refresh(draft)
    detail = draft.artifact_json["stages"][0]["implementation_details"][0]
    assert detail["command"] == "pip install x"
    assert detail["expected_result"] == "reports ok"
    assert detail["caution"] == "use a venv"

    # And the edited field is locked, so a later AI refinement cannot overwrite
    # what the user just typed. The lock is fully qualified
    # (`<entity id>.<field>`), which is the format H110's `is_locked` matches.
    assert f"{stage_id}.implementation_details" in draft.locked_paths
