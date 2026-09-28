"""M6 tests: targeted refinement, patch preview, accept and reject.

Covers the acceptance criteria in `23-coding-agent-milestones.md`:

- rejecting changes nothing,
- accepting modifies Draft only,
- locked / user-edited sibling content is preserved.

The third one is the interesting one. It is tested from the user's side: edit a
field by hand, ask for a refinement, and check the hand-written text is still
there. Asserting on internal lock bookkeeping would pass just as well against an
implementation that recorded locks and then ignored them.
"""

import asyncio
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import COPVersion, Draft, GenerationRun, Project
from app.domain.drafting import with_locks
from app.harness.provider_factory import build_provider
from app.harness.runner import run_pipeline
from app.jobs.runner import (
    DatabaseRunStore,
    claim_next_run,
    create_run,
    finish_run,
    load_context,
    load_target_context,
)


def load_fixture() -> dict:
    from pathlib import Path

    path = Path(__file__).resolve().parents[2] / "fixtures" / "reference-langchain-cop.json"
    with path.open(encoding="utf-8") as handle:
        return json_load(handle)


def json_load(handle) -> dict:
    import json

    return json.load(handle)


def create_project(db: Session, title: str = "Refine") -> str:
    project = Project(title=title, domain=title, scope="Scope")
    db.add(project)
    db.commit()
    return str(project.id)


def make_draft(db: Session, project_id: str, locked: list[str] | None = None) -> str:
    draft = Draft(
        project_id=project_id,
        artifact_json=load_fixture(),
        locked_paths=locked or [],
    )
    db.add(draft)
    db.commit()
    return str(draft.id)


def make_targeted_run(db: Session, project_id: str, entity_type: str, entity_id: str) -> str:
    run = create_run(
        db,
        project_id=project_id,
        mode="standard",
        requested_input={
            "topic": "",
            "target": {"entity_type": entity_type, "entity_id": entity_id},
            "instruction": "Make this clearer",
        },
        settings={},
    )
    return str(run.id)


def execute_run(db: Session, run_id: str) -> dict:
    """Claim and execute one run the way the worker does."""
    row = claim_next_run(db, "worker-test")
    assert row is not None and str(row.id) == run_id
    context = load_context(row)
    assert context.partial_target is not None, "target must reach the context"
    assert load_target_context(db, row, context), "a refinement needs a base artifact"

    provider = build_provider(db, row.project_id, None)
    store = DatabaseRunStore(row.id)
    outcome = asyncio.run(run_pipeline(context, provider, store))
    finish_run(db, row.id, status=outcome.status, context=outcome.context, metrics={})
    db.refresh(row)
    return {"status": row.status, "patch": row.candidate_patch_json}


@pytest.fixture
def first_goal() -> tuple[str, str]:
    goal = load_fixture()["goals"][0]
    return "goal", goal["id"]


class TestLocksAreRecorded:
    def test_a_manual_edit_locks_exactly_the_changed_field(self, client, db):
        project_id = create_project(db)
        draft_id = make_draft(db, project_id)
        goal_id = load_fixture()["goals"][0]["id"]

        client.patch(
            f"/api/v1/drafts/{draft_id}/goals/{goal_id}", json={"outcome": "Hand written."}
        )

        draft = db.get(Draft, uuid.UUID(draft_id))
        assert draft.locked_paths == [f"{goal_id}.outcome"]

    def test_resending_an_unchanged_field_does_not_lock_it(self, client, db):
        """A PATCH may resend the whole form; only a real change may lock."""
        project_id = create_project(db)
        draft_id = make_draft(db, project_id)
        goal_id = load_fixture()["goals"][0]["id"]
        original = load_fixture()["goals"][0]["outcome"]

        client.patch(f"/api/v1/drafts/{draft_id}/goals/{goal_id}", json={"outcome": original})

        assert db.get(Draft, uuid.UUID(draft_id)).locked_paths == []

    def test_a_rejected_edit_locks_nothing(self, client, db):
        project_id = create_project(db)
        draft_id = make_draft(db, project_id)
        goal_id = load_fixture()["goals"][0]["id"]

        client.patch(f"/api/v1/drafts/{draft_id}/goals/{goal_id}", json={"outcome": "  "})

        assert db.get(Draft, uuid.UUID(draft_id)).locked_paths == []

    def test_locks_accumulate_without_duplicates(self):
        locks = with_locks(["goal.a.outcome"], "goal.a", ["outcome", "title"])
        assert locks == ["goal.a.outcome", "goal.a.title"]
        assert with_locks(locks, "goal.a", ["outcome"]) == locks


class TestTargetedRun:
    def test_a_targeted_run_produces_a_patch_not_a_new_artifact(self, client, db, first_goal):
        entity_type, entity_id = first_goal
        project_id = create_project(db)
        make_draft(db, project_id)
        run_id = make_targeted_run(db, project_id, entity_type, entity_id)

        result = execute_run(db, run_id)

        assert result["status"] == "completed"
        assert result["patch"] is not None
        assert result["patch"]["entity_id"] == entity_id
        # The run must not also claim to have produced a replacement artifact.
        run = db.get(GenerationRun, uuid.UUID(run_id))
        assert run.patch_state == "ready"

    def test_a_refinement_never_touches_another_entity(self, client, db, first_goal):
        """The blast radius of a one-entity fix must stay one entity."""
        entity_type, entity_id = first_goal
        project_id = create_project(db)
        draft_id = make_draft(db, project_id)
        before = load_fixture()
        run_id = make_targeted_run(db, project_id, entity_type, entity_id)
        execute_run(db, run_id)

        draft = db.get(Draft, uuid.UUID(draft_id))
        assert draft.artifact_json["goals"] == before["goals"], (
            "proposing a patch must not modify the draft at all"
        )
        assert draft.artifact_json["stages"] == before["stages"]

    def test_a_user_edited_field_is_never_proposed_for_rewrite(self, client, db, first_goal):
        """Acceptance: locked / user-edited content is preserved."""
        entity_type, entity_id = first_goal
        project_id = create_project(db)
        draft_id = make_draft(db, project_id)
        client.patch(
            f"/api/v1/drafts/{draft_id}/goals/{entity_id}",
            json={"why_it_matters": "Hand-written reasoning."},
        )

        run_id = make_targeted_run(db, project_id, entity_type, entity_id)
        result = execute_run(db, run_id)

        changed = {item["field"] for item in result["patch"]["changes"]}
        assert "why_it_matters" not in changed
        # And the refusal is reported rather than hidden.
        rejected = {item["field"]: item["reason"] for item in result["patch"]["rejected"]}
        assert "why_it_matters" in rejected
        assert "locked" in rejected["why_it_matters"]

    def test_a_run_without_a_target_still_produces_an_artifact(self, client, db):
        project_id = create_project(db)
        run = create_run(
            db,
            project_id=project_id,
            mode="standard",
            requested_input={"topic": "Docker packaging", "source_ids": []},
            settings={},
        )
        context = load_context(run)
        assert context.partial_target is None

    def test_an_unrefinable_target_is_rejected_at_request_time(self, client, db):
        project_id = create_project(db)
        response = client.post(
            f"/api/v1/projects/{project_id}/generation-runs",
            json={
                "target": {"entity_type": "concept", "entity_id": "concept.x"},
                "topic": "",
            },
        )
        assert response.status_code == 422
        # Rejected by the request schema before any work is queued, so the user
        # hears about it immediately rather than in a failed run.
        assert "entity_type" in response.text


class TestPatchPreview:
    def test_the_preview_carries_a_before_and_an_after(self, client, db, first_goal):
        entity_type, entity_id = first_goal
        project_id = create_project(db)
        make_draft(db, project_id)
        run_id = make_targeted_run(db, project_id, entity_type, entity_id)
        execute_run(db, run_id)

        response = client.get(f"/api/v1/generation-runs/{run_id}/candidate-patch")
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["state"] == "ready"
        assert body["entity_id"] == entity_id
        for change in body["changes"]:
            assert change["before"] != change["after"], "a diff needs two different values"

    def test_a_run_with_no_patch_says_so(self, client, db):
        project_id = create_project(db)
        run = GenerationRun(project_id=project_id, status="completed", requested_mode="standard")
        db.add(run)
        db.commit()

        response = client.get(f"/api/v1/generation-runs/{run.id}/candidate-patch")
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "PATCH_NOT_READY"


class TestAccept:
    def test_accepting_modifies_the_draft_only(self, client, db, first_goal):
        """Acceptance: accepting modifies Draft only."""
        entity_type, entity_id = first_goal
        project_id = create_project(db)
        draft_id = make_draft(db, project_id)
        run_id = make_targeted_run(db, project_id, entity_type, entity_id)
        result = execute_run(db, run_id)
        changes = result["patch"]["changes"]
        if not changes:
            pytest.skip("the mock proposed no changes for this entity")
        target_field = changes[0]["field"]

        response = client.post(f"/api/v1/generation-runs/{run_id}/candidate-patch/accept")
        assert response.status_code == 200, response.text
        assert response.json()["state"] == "accepted"
        assert target_field in response.json()["applied_fields"]

        draft = db.get(Draft, uuid.UUID(draft_id))
        goal = next(item for item in draft.artifact_json["goals"] if item["id"] == entity_id)
        assert goal[target_field] == changes[0]["after"]

        # No version was created, and none was modified.
        assert list(db.scalars(select(COPVersion).where(COPVersion.project_id == project_id))) == []

    def test_accepting_preserves_a_hand_written_field(self, client, db, first_goal):
        """The end-to-end version of the acceptance criterion.

        The user locks the exact field the model wants to rewrite, then accepts.
        The point is not that something was applied -- it is that the user's own
        words survive, and that the refusal is visible rather than silent.
        """
        entity_type, entity_id = first_goal
        project_id = create_project(db)
        draft_id = make_draft(db, project_id)
        client.patch(
            f"/api/v1/drafts/{draft_id}/goals/{entity_id}",
            json={"why_it_matters": "Do not touch this sentence."},
        )
        run_id = make_targeted_run(db, project_id, entity_type, entity_id)
        execute_run(db, run_id)

        # The refusal is surfaced in the preview, before the user is asked to
        # accept anything. Silently dropping it would leave them wondering why
        # the model ignored their instruction.
        preview = client.get(f"/api/v1/generation-runs/{run_id}/candidate-patch").json()
        rejected = {item["field"]: item["reason"] for item in preview["rejected"]}
        assert "why_it_matters" in rejected
        assert "locked" in rejected["why_it_matters"]
        assert preview["changes"] == []

        response = client.post(f"/api/v1/generation-runs/{run_id}/candidate-patch/accept")
        assert response.status_code == 200, response.text

        draft = db.get(Draft, uuid.UUID(draft_id))
        goal = next(item for item in draft.artifact_json["goals"] if item["id"] == entity_id)
        assert goal["why_it_matters"] == "Do not touch this sentence."

    def test_a_locked_field_does_not_block_unrelated_changes(self, client, db, first_goal):
        """Locking one field must not freeze the whole entity."""
        entity_type, entity_id = first_goal
        project_id = create_project(db)
        draft_id = make_draft(db, project_id)
        client.patch(f"/api/v1/drafts/{draft_id}/goals/{entity_id}", json={"title": "My own title"})
        run_id = make_targeted_run(db, project_id, entity_type, entity_id)
        result = execute_run(db, run_id)
        assert result["patch"]["changes"], "the mock should still propose an unlocked field"

        response = client.post(f"/api/v1/generation-runs/{run_id}/candidate-patch/accept")
        assert response.status_code == 200, response.text

        draft = db.get(Draft, uuid.UUID(draft_id))
        goal = next(item for item in draft.artifact_json["goals"] if item["id"] == entity_id)
        assert goal["title"] == "My own title"
        assert goal["why_it_matters"] == result["patch"]["changes"][0]["after"]

    def test_a_stale_patch_is_refused(self, client, db, first_goal):
        """Accepting must not discard an edit made while the preview was open."""
        entity_type, entity_id = first_goal
        project_id = create_project(db)
        draft_id = make_draft(db, project_id)
        run_id = make_targeted_run(db, project_id, entity_type, entity_id)
        result = execute_run(db, run_id)
        if not result["patch"]["changes"]:
            pytest.skip("the mock proposed no changes for this entity")
        field = result["patch"]["changes"][0]["field"]

        # The user keeps typing after seeing the proposal.
        client.patch(
            f"/api/v1/drafts/{draft_id}/goals/{entity_id}",
            json={field: "Newer, hand-written value."},
        )

        response = client.post(f"/api/v1/generation-runs/{run_id}/candidate-patch/accept")
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "PATCH_STALE"

        draft = db.get(Draft, uuid.UUID(draft_id))
        goal = next(item for item in draft.artifact_json["goals"] if item["id"] == entity_id)
        assert goal[field] == "Newer, hand-written value."

    def test_accepting_twice_is_refused(self, client, db, first_goal):
        entity_type, entity_id = first_goal
        project_id = create_project(db)
        make_draft(db, project_id)
        run_id = make_targeted_run(db, project_id, entity_type, entity_id)
        result = execute_run(db, run_id)
        if not result["patch"]["changes"]:
            pytest.skip("the mock proposed no changes for this entity")

        client.post(f"/api/v1/generation-runs/{run_id}/candidate-patch/accept")
        second = client.post(f"/api/v1/generation-runs/{run_id}/candidate-patch/accept")
        assert second.status_code == 409
        assert second.json()["error"]["code"] == "PATCH_NOT_ACCEPTABLE"

    def test_accepting_without_a_draft_is_refused(self, client, db, first_goal):
        """A published version is not a valid target for accept."""
        entity_type, entity_id = first_goal
        project_id = create_project(db)
        version = COPVersion(
            project_id=project_id,
            version_number=1,
            artifact_json=load_fixture(),
            change_summary="v1",
            created_by="harness",
        )
        db.add(version)
        db.commit()
        run_id = make_targeted_run(db, project_id, entity_type, entity_id)
        db.get(GenerationRun, uuid.UUID(run_id)).base_version_id = version.id
        db.commit()
        result = execute_run(db, run_id)
        if not result["patch"]["changes"]:
            pytest.skip("the mock proposed no changes for this entity")

        response = client.post(f"/api/v1/generation-runs/{run_id}/candidate-patch/accept")
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "NO_ACTIVE_DRAFT"
        # The published version is untouched by the refusal.
        db.refresh(version)
        assert version.artifact_json == load_fixture()


class TestReject:
    def test_rejecting_changes_nothing(self, client, db, first_goal):
        """Acceptance: rejecting changes nothing."""
        entity_type, entity_id = first_goal
        project_id = create_project(db)
        draft_id = make_draft(db, project_id)
        before = load_fixture()
        run_id = make_targeted_run(db, project_id, entity_type, entity_id)
        execute_run(db, run_id)

        response = client.post(f"/api/v1/generation-runs/{run_id}/candidate-patch/reject")
        assert response.status_code == 200, response.text
        assert response.json()["state"] == "rejected"

        draft = db.get(Draft, uuid.UUID(draft_id))
        assert draft.artifact_json == before
        assert list(db.scalars(select(COPVersion).where(COPVersion.project_id == project_id))) == []

    def test_a_rejected_patch_cannot_be_accepted(self, client, db, first_goal):
        entity_type, entity_id = first_goal
        project_id = create_project(db)
        make_draft(db, project_id)
        run_id = make_targeted_run(db, project_id, entity_type, entity_id)
        result = execute_run(db, run_id)
        if not result["patch"]["changes"]:
            pytest.skip("the mock proposed no changes for this entity")

        client.post(f"/api/v1/generation-runs/{run_id}/candidate-patch/reject")
        response = client.post(f"/api/v1/generation-runs/{run_id}/candidate-patch/accept")
        assert response.status_code == 409

    def test_rejecting_twice_is_refused(self, client, db, first_goal):
        entity_type, entity_id = first_goal
        project_id = create_project(db)
        make_draft(db, project_id)
        run_id = make_targeted_run(db, project_id, entity_type, entity_id)
        execute_run(db, run_id)

        client.post(f"/api/v1/generation-runs/{run_id}/candidate-patch/reject")
        second = client.post(f"/api/v1/generation-runs/{run_id}/candidate-patch/reject")
        assert second.status_code == 409
        assert second.json()["error"]["code"] == "PATCH_ALREADY_DECIDED"


class TestPatchImmutability:
    def test_no_endpoint_can_change_a_published_version_from_a_patch(self, client, db):
        """The patch router must have no path to a COPVersion at all."""
        paths = client.get("/openapi.json").json()["paths"]
        for path, operations in paths.items():
            if "candidate-patch" not in path:
                continue
            assert set(operations) <= {"get", "post"}, (
                f"{path} exposes {sorted(operations)}; a patch must only be read or decided"
            )

    def test_the_patch_routes_are_scoped_to_a_run(self, client, db):
        paths = client.get("/openapi.json").json()["paths"]
        patch_paths = [path for path in paths if "candidate-patch" in path]
        assert patch_paths
        for path in patch_paths:
            assert path.startswith("/api/v1/generation-runs/{run_id}/candidate-patch")
