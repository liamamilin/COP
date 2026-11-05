"""Manual resume: real PostgreSQL transactions, fake models, no paid requests."""

import asyncio
import copy
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AppSetting, COPVersion, Draft, GenerationRun, Project
from app.harness.providers import MockProvider, ProviderError
from app.jobs import worker
from app.jobs.events import read_events
from app.jobs.resumption import recovery_view, resume_run
from app.jobs.runner import claim_next_run, create_run


class FailAtCore(MockProvider):
    async def generate_structured(self, **kwargs):
        if kwargs["schema"]["title"] == "H60CanonicalizeConceptsOperations":
            raise ProviderError("PROVIDER_TIMEOUT", "Simulated H60 timeout")
        return await super().generate_structured(**kwargs)


@pytest.fixture
def failed_run(db, monkeypatch):
    project = Project(title="Resume test", domain="CSV", scope="Read CSV")
    db.add(project)
    db.commit()
    run = create_run(
        db,
        project_id=project.id,
        mode="fast",
        requested_input={"topic": "Read CSV", "source_ids": [], "web_search": False},
        settings={
            "provider": {"type": "mock", "mock_scenario": "success", "timeout": 60},
            "language": "en",
            "generation_depth": "fast",
        },
    )
    monkeypatch.setattr(worker, "build_provider_from_snapshot", lambda _: FailAtCore())
    assert asyncio.run(worker.execute_run())
    db.refresh(run)
    assert run.status == "failed", run.error_message
    assert run.error_code == "PROVIDER_TIMEOUT"
    assert run.checkpoint_json["completed_steps"][-1] == "H50"
    return run


def test_resume_reuses_h00_to_h50_and_does_not_publish(db, client, monkeypatch, failed_run):
    run = failed_run
    original = copy.deepcopy(run.checkpoint_json)
    info = client.get(f"/api/v1/generation-runs/{run.id}/progress").json()["recovery"]
    assert info["allowed"] and info["from_step"] == "H60"
    response = client.post(
        f"/api/v1/generation-runs/{run.id}/resume",
        json={"expected_attempt": 1, "timeout_seconds": 180},
    )
    assert response.status_code == 200, response.text
    db.refresh(run)
    boundary = recovery_view(db, run)["event_cursor"]
    assert run.status == "queued"
    assert run.error_code is None and run.completed_at is None and run.worker_id is None
    assert run.candidate_artifact_json is None
    assert run.model_config_json["provider"]["timeout"] == 180
    assert run.checkpoint_json["settings"]["provider"]["timeout"] == 180

    monkeypatch.setattr(worker, "build_provider_from_snapshot", lambda _: MockProvider())
    assert asyncio.run(worker.execute_run())
    db.refresh(run)
    assert run.status == "completed", run.error_message
    starts = [
        e.step for e in read_events(db, run.id, after=boundary) if e.event_type == "step.started"
    ]
    assert starts[0] == "H60"
    assert not set(starts) & {"H00", "H10", "H20", "H30", "H40", "H50"}
    assert {"H120", "H130"} <= set(starts)
    assert run.checkpoint_json["stage_drafts"] == original["stage_drafts"]
    assert not list(db.scalars(select(COPVersion)))
    assert not list(db.scalars(select(Draft)))
    history = recovery_view(db, run)["history"]
    assert history[0]["error_code"] == "PROVIDER_TIMEOUT"
    assert history[0]["metrics"]["provider_calls"] > 0


def test_duplicate_resume_is_idempotent_even_after_next_failure(db, failed_run):
    run = failed_run
    before = copy.deepcopy(run.checkpoint_json)
    resume_run(db, run.id, expected_attempt=1)
    resume_run(db, run.id, expected_attempt=1)
    assert recovery_view(db, run)["attempt"] == 2
    assert run.checkpoint_json == before
    # Fail again; a delayed duplicate click from attempt 1 must not start attempt 3.
    assert asyncio.run(worker.execute_run())
    db.refresh(run)
    assert run.status == "failed"
    resume_run(db, run.id, expected_attempt=1)
    db.refresh(run)
    assert run.status == "failed"
    assert len(recovery_view(db, run)["history"]) == 1
    resume_run(db, run.id, expected_attempt=2)
    assert len(recovery_view(db, run)["history"]) == 2


def test_concurrent_clicks_only_queue_one_attempt(engine, db, failed_run):
    run_id = failed_run.id

    def click():
        with Session(engine) as session:
            return resume_run(session, run_id, expected_attempt=1).status

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(lambda _: click(), range(2))) == ["queued", "queued"]
    db.expire_all()
    assert len(recovery_view(db, db.get(GenerationRun, run_id))["history"]) == 1
    assert claim_next_run(db, "first") is not None
    assert claim_next_run(db, "second") is None


@pytest.mark.parametrize(
    "status", ["running", "queued", "completed", "cancelled", "needs_attention"]
)
def test_terminal_and_active_states_cannot_be_resumed(client, db, failed_run, status):
    failed_run.status = status
    db.commit()
    response = client.post(
        f"/api/v1/generation-runs/{failed_run.id}/resume", json={"expected_attempt": 1}
    )
    assert response.status_code == 409


@pytest.mark.parametrize("damage", ["missing_marker", "partial_stages", "unsafe", "targeted"])
def test_bad_checkpoints_and_unsafe_runs_are_rejected(client, db, failed_run, damage):
    checkpoint = copy.deepcopy(failed_run.checkpoint_json)
    if damage == "missing_marker":
        checkpoint["completed_steps"].remove("H30")
    elif damage == "partial_stages":
        checkpoint["stage_drafts"].pop()
    elif damage == "unsafe":
        failed_run.retry_safe = False
    else:
        failed_run.requested_sections_json = {"target": {"entity_type": "stage", "entity_id": "s"}}
    failed_run.checkpoint_json = checkpoint
    db.commit()
    info = client.get(f"/api/v1/generation-runs/{failed_run.id}/progress").json()["recovery"]
    assert not info["allowed"]
    assert (
        client.post(
            f"/api/v1/generation-runs/{failed_run.id}/resume", json={"expected_attempt": 1}
        ).status_code
        == 409
    )


def test_worker_uses_original_model_and_sources(db, client, monkeypatch, failed_run):
    checkpoint = copy.deepcopy(failed_run.checkpoint_json)
    checkpoint["source_bundle"] = [{"id": "original", "type": "text", "text": "original text"}]
    failed_run.checkpoint_json = checkpoint
    # Changing app defaults must not cause a paid call or alter the in-progress COP.
    app = db.get(AppSetting, 1)
    if app is None:
        app = AppSetting(id=1, settings_json={})
        db.add(app)
    app.settings_json = {
        "provider": {
            "type": "openai_compatible",
            "base_url": "https://invalid",
            "model": "changed-model",
        }
    }
    db.commit()
    captured = []

    def build(snapshot):
        captured.append(snapshot)
        assert snapshot["provider"]["type"] == "mock"
        return MockProvider()

    monkeypatch.setattr(worker, "build_provider_from_snapshot", build)
    resume_run(db, failed_run.id, expected_attempt=1)
    assert asyncio.run(worker.execute_run())
    db.refresh(failed_run)
    assert failed_run.status == "completed", failed_run.error_message
    assert failed_run.checkpoint_json["source_bundle"] == checkpoint["source_bundle"]
    assert captured


def test_old_terminal_events_are_not_replayed_as_current(client, db, monkeypatch, failed_run):
    resume_run(db, failed_run.id, expected_attempt=1)
    boundary = recovery_view(db, failed_run)["event_cursor"]
    monkeypatch.setattr(worker, "build_provider_from_snapshot", lambda _: MockProvider())
    assert asyncio.run(worker.execute_run())
    with client.stream(
        "GET", f"/api/v1/generation-runs/{failed_run.id}/events", headers={"Last-Event-ID": "1"}
    ) as response:
        body = "".join(response.iter_text())
    assert "event: run.failed" not in body
    assert "event: run.completed" in body
    assert f"id: {boundary - 1}\n" not in body
    progress = client.get(f"/api/v1/generation-runs/{failed_run.id}/progress").json()
    assert all(p["status"] == "done" for p in progress["phases"])


def test_failed_partial_candidate_is_not_available(client, db, failed_run):
    failed_run.candidate_artifact_json = {"partial": True}
    db.commit()
    assert not client.get(f"/api/v1/generation-runs/{failed_run.id}/progress").json()[
        "candidate_available"
    ]
    assert client.get(f"/api/v1/generation-runs/{failed_run.id}/candidate").status_code == 409


def test_resume_unknown_run_is_404(client):
    assert (
        client.post(
            f"/api/v1/generation-runs/{uuid.uuid4()}/resume", json={"expected_attempt": 1}
        ).status_code
        == 404
    )


@pytest.mark.parametrize(
    "override", [{"model": "other-model"}, {"source_ids": []}, {"timeout_seconds": 601}]
)
def test_resume_cannot_change_content_settings(client, db, failed_run, override):
    before = copy.deepcopy(failed_run.checkpoint_json)
    response = client.post(
        f"/api/v1/generation-runs/{failed_run.id}/resume", json={"expected_attempt": 1, **override}
    )
    assert response.status_code == 422
    db.refresh(failed_run)
    assert failed_run.status == "failed" and failed_run.checkpoint_json == before


def test_resumed_progress_preserves_done_steps_without_old_active_step(client, db, failed_run):
    resume_run(db, failed_run.id, expected_attempt=1)
    progress = client.get(f"/api/v1/generation-runs/{failed_run.id}/progress").json()
    phases = {p["key"]: p["status"] for p in progress["phases"]}
    assert phases["processes"] == "done"
    assert phases["concepts"] == "pending"
    assert not progress["candidate_available"]


def test_partial_outputs_without_a_completion_marker_are_recomputed(db, monkeypatch, failed_run):
    checkpoint = copy.deepcopy(failed_run.checkpoint_json)
    checkpoint["concepts"] = [{"key": "partial-concept"}]
    checkpoint["operations"] = [{"key": "partial-operation"}]
    failed_run.checkpoint_json = checkpoint
    db.commit()
    resume_run(db, failed_run.id, expected_attempt=1)
    boundary = recovery_view(db, failed_run)["event_cursor"]
    monkeypatch.setattr(worker, "build_provider_from_snapshot", lambda _: MockProvider())
    assert asyncio.run(worker.execute_run())
    db.refresh(failed_run)
    assert failed_run.status == "completed"
    starts = [
        e.step
        for e in read_events(db, failed_run.id, after=boundary)
        if e.event_type == "step.started"
    ]
    assert starts[0] == "H60"
    assert failed_run.checkpoint_json["concepts"] != checkpoint["concepts"]
