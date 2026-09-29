"""Generation run API tests.

These exercise the real database queue, worker claim, event stream,
cancellation, and crash recovery against PostgreSQL, because that is where the
behaviour under test lives (`FOR UPDATE SKIP LOCKED`, the unique sequence
constraint, stale-run recovery). The V1 spec makes PostgreSQL the only
normative database, so there is no SQLite fallback to test against.

Skipped automatically when `TEST_DATABASE_URL` is not set.
"""

import asyncio
import os
import subprocess
import sys
import time
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.api.generations import TERMINAL_STATUSES
from app.db.models import GenerationRun, Project
from app.db.session import SessionLocal
from app.harness.provider_factory import build_provider
from app.harness.runner import build_metrics, run_pipeline
from app.jobs.events import append_event, read_events
from app.jobs.runner import (
    DatabaseRunStore,
    claim_next_run,
    create_run,
    finish_run,
    load_context,
    load_source_bundle,
    recover_stale_runs,
    store_checkpoint,
)

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "")


def require_database() -> str:
    """Fail loudly instead of silently skipping when a database test must run.

    These tests cover queue claiming and recovery, which is the core of the
    persisted Harness. Skipping them by default in CI would leave the milestone
    looking green while its central mechanism is never executed.
    """
    if not TEST_DATABASE_URL:
        pytest.fail(
            "TEST_DATABASE_URL must be set to run database tests; "
            "see backend/tests/conftest.py for the expected value"
        )
    return TEST_DATABASE_URL


def create_project(db: Session, title: str) -> str:
    project = Project(title=title, domain=title, scope="Ship a containerized service")
    db.add(project)
    db.commit()
    return str(project.id)


def start_run(client: TestClient, db: Session, title: str, **body) -> str:
    project_id = create_project(db, title)
    payload = {"topic": "Docker Application Packaging", "mode": "standard", **body}
    response = client.post(f"/api/v1/projects/{project_id}/generation-runs", json=payload)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def execute_one_run(db: Session, run_id: str, *, worker: str = "worker-test") -> dict:
    """Claim and execute a single run the way the worker process does.

    Returns the run's recorded metrics.
    """
    row = claim_next_run(db, worker)
    assert row is not None, "expected a queued run to claim"
    assert str(row.id) == run_id

    context = load_context(row)
    context.source_bundle = load_source_bundle(db, row)
    provider = build_provider(db, row.project_id, None)
    store = DatabaseRunStore(row.id)

    outcome = asyncio.run(run_pipeline(context, provider, store))
    finish_run(
        db,
        row.id,
        status=outcome.status,
        context=outcome.context,
        metrics=build_metrics(outcome.context, outcome.provider_calls, started=0.0),
    )
    db.refresh(row)
    return dict(row.metrics_json or {})


def create_project_in_session(title: str) -> str:
    """Create a project on a fresh session, for tests that bypass the API client."""
    with SessionLocal() as session:
        project = Project(title=title, domain=title, scope="s")
        session.add(project)
        session.commit()
        return str(project.id)


async def wait_for_terminal(run_id: str, *, timeout: float = 20.0) -> str:
    """Poll a run until terminal, the way a client without SSE would."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with SessionLocal() as session:
            row = session.get(GenerationRun, uuid.UUID(run_id))
            if row is not None and row.status in TERMINAL_STATUSES:
                return row.status
        await asyncio.sleep(0.2)
    raise AssertionError(f"run {run_id} did not finish within {timeout}s")


def test_the_worker_process_drives_a_queued_run_to_completion() -> None:
    require_database()
    """Exercise the real worker loop, not a reimplementation of it.

    The worker runs in a subprocess against the test database with a very short
    poll interval, exactly as Docker Compose starts it. This is the only test
    that proves the shipped entry point works, rather than the same calls
    re-assembled inside pytest.
    """
    project_id = create_project_in_session("Worker Subprocess")
    with SessionLocal() as session:
        run = create_run(
            session,
            project_id=uuid.UUID(project_id),
            mode="standard",
            requested_input={
                "topic": "Docker Application Packaging",
                "scope_hint": "",
                "target_outcomes": [],
                "learner_level": "new",
                "source_ids": [],
            },
            settings={"language": "en", "generation_depth": "fast", "practice_mode": "priority"},
        )
        run_id = str(run.id)

    env = {
        **os.environ,
        "DATABASE_URL": TEST_DATABASE_URL,
        "APP_SECRET": "worker-subprocess-secret",
        "COP_PROVIDER_MODE": "mock",
        "WORKER_POLL_SECONDS": "0.2",
    }
    process = subprocess.Popen(
        [sys.executable, "-m", "app.jobs.worker"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        status = asyncio.run(wait_for_terminal(run_id, timeout=45))
    finally:
        process.terminate()
        output, _ = process.communicate(timeout=15)

    assert status == "completed", output

    with SessionLocal() as session:
        finished = session.get(GenerationRun, uuid.UUID(run_id))
        artifact = finished.candidate_artifact_json
        metrics = finished.metrics_json
        worker_id = finished.worker_id

    assert artifact is not None
    assert artifact["goals"] and artifact["main_processes"] and artifact["stages"]
    assert metrics["provider_calls"] > 0
    assert worker_id, "the run should record which worker executed it"
    assert "worker started" in output


def mark_terminal(db: Session, run_id: str, status: str) -> None:
    db.execute(
        update(GenerationRun).where(GenerationRun.id == uuid.UUID(run_id)).values(status=status)
    )
    db.commit()


def test_starting_a_run_requires_a_topic_or_source(client: TestClient, db: Session) -> None:
    require_database()
    project = client.post(
        "/api/v1/projects", json={"title": "Empty", "domain": "Empty", "scope": "s"}
    ).json()

    response = client.post(f"/api/v1/projects/{project['id']}/generation-runs", json={})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "HARNESS_INTAKE_INCOMPLETE"


def test_a_run_records_explicit_web_search_opt_in(client: TestClient, db: Session) -> None:
    require_database()
    run_id = start_run(
        client,
        db,
        "Web Research",
        web_search=True,
        settings_override={
            "generation": {"language": "zh-CN", "generation_depth": "fast"}
        },
    )

    row = db.get(GenerationRun, uuid.UUID(run_id))
    assert row is not None
    assert row.requested_sections_json["web_search"] is True
    context = load_context(row)
    assert context.settings["language"] == "zh-CN"
    assert context.settings["generation_depth"] == "fast"


def test_a_run_is_queued_and_then_claimed_by_exactly_one_worker(
    client: TestClient, db: Session
) -> None:
    require_database()
    run_id = start_run(client, db, "Docker Packaging")

    assert client.get(f"/api/v1/generation-runs/{run_id}").json()["status"] == "queued"

    claimed = claim_next_run(db, "worker-a")
    assert claimed is not None
    assert str(claimed.id) == run_id
    assert claim_next_run(db, "worker-b") is None, "a claimed run must not be double-claimed"

    status = client.get(f"/api/v1/generation-runs/{run_id}").json()
    assert status["status"] == "running"
    assert status["worker_id"] == "worker-a"


def test_worker_completes_a_run_and_publishes_a_valid_candidate(
    client: TestClient, db: Session
) -> None:
    require_database()
    """The M4 acceptance path: topic -> run -> progress -> validated candidate."""
    run_id = start_run(client, db, "Docker Packaging")
    metrics = execute_one_run(db, run_id)

    assert metrics["goals"] > 0
    assert metrics["provider_calls"] > 0
    assert metrics["retried_calls"] == 0

    final = client.get(f"/api/v1/generation-runs/{run_id}").json()
    assert final["status"] == "completed", final
    assert final["metrics"]["goals"] > 0
    assert final["metrics"]["provider_calls"] > 0

    candidate = client.get(f"/api/v1/generation-runs/{run_id}/candidate").json()
    artifact = candidate["artifact"]
    assert artifact["schema_version"] == "0.1"
    assert artifact["goals"] and artifact["main_processes"] and artifact["stages"]

    # Progress is reported as user-facing phases, all finished.
    progress = client.get(f"/api/v1/generation-runs/{run_id}/progress").json()
    assert progress["candidate_available"] is True
    assert [phase["key"] for phase in progress["phases"]] == [
        "scope",
        "sources",
        "goals",
        "processes",
        "concepts",
        "compression",
        "learning",
        "assembly",
        "quality",
        "finalize",
    ]
    assert all(phase["status"] == "done" for phase in progress["phases"]), progress["phases"]


def test_candidate_is_not_readable_before_the_run_finishes(client: TestClient, db: Session) -> None:
    require_database()
    run_id = start_run(client, db, "Pending Candidate")

    response = client.get(f"/api/v1/generation-runs/{run_id}/candidate")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CANDIDATE_NOT_READY"


def test_event_stream_replays_history_then_closes_on_terminal_state(
    client: TestClient, db: Session
) -> None:
    require_database()
    run_id = start_run(client, db, "Event Stream")
    run_uuid = uuid.UUID(run_id)

    append_event(db, run_uuid, "run.queued", payload={"mode": "standard"})
    append_event(db, run_uuid, "step.started", step="H00", payload={"step": "H00"})
    append_event(db, run_uuid, "run.completed", payload={"status": "completed", "goals": 3})
    mark_terminal(db, run_id, "completed")

    with client.stream("GET", f"/api/v1/generation-runs/{run_id}/events") as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        body = "".join(response.iter_text())

    # A reconnecting client must receive the full history, not an empty stream.
    assert "event: run.queued" in body
    assert "event: run.completed" in body
    assert '"goals": 3' in body


def test_event_stream_honours_last_event_id_for_reconnect(client: TestClient, db: Session) -> None:
    require_database()
    run_id = start_run(client, db, "Reconnect")
    run_uuid = uuid.UUID(run_id)
    first = append_event(db, run_uuid, "run.queued", payload={"mode": "standard"})
    append_event(db, run_uuid, "run.completed", payload={"status": "completed"})
    mark_terminal(db, run_id, "completed")

    assert first is not None
    with client.stream(
        "GET",
        f"/api/v1/generation-runs/{run_id}/events",
        headers={"Last-Event-ID": str(first.sequence)},
    ) as response:
        body = "".join(response.iter_text())

    # Only the unseen tail is replayed.
    assert "event: run.queued" not in body
    assert "event: run.completed" in body


def test_events_endpoint_returns_404_for_an_unknown_run(client: TestClient, db: Session) -> None:
    require_database()
    assert client.get(f"/api/v1/generation-runs/{uuid.uuid4()}/events").status_code == 404


def test_cancellation_is_recorded_and_acknowledges_a_queued_run(
    client: TestClient, db: Session
) -> None:
    require_database()
    run_id = start_run(client, db, "Cancel")

    first = client.post(f"/api/v1/generation-runs/{run_id}/cancel")
    assert first.status_code == 200
    assert first.json()["cancel_requested"] is True

    # Repeating the request is harmless rather than an error.
    assert client.post(f"/api/v1/generation-runs/{run_id}/cancel").status_code == 200
    assert db.get(GenerationRun, uuid.UUID(run_id)).cancel_requested is True


def test_cancelling_a_finished_run_is_rejected(client: TestClient, db: Session) -> None:
    require_database()
    run_id = start_run(client, db, "Already Done")
    mark_terminal(db, run_id, "completed")

    response = client.post(f"/api/v1/generation-runs/{run_id}/cancel")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "GENERATION_ALREADY_TERMINAL"


def test_a_stale_running_run_is_requeued_for_another_worker(
    client: TestClient, db: Session
) -> None:
    require_database()
    """A crashed worker must not strand a run."""
    from datetime import UTC, datetime, timedelta

    run_id = start_run(client, db, "Stale")
    stale = datetime.now(UTC) - timedelta(hours=1)
    db.execute(
        update(GenerationRun)
        .where(GenerationRun.id == uuid.UUID(run_id))
        .values(status="running", worker_id="dead-worker", heartbeat_at=stale, started_at=stale)
    )
    db.commit()

    assert recover_stale_runs(db) == 1

    recovered = db.get(GenerationRun, uuid.UUID(run_id))
    assert recovered.status == "queued"
    assert recovered.worker_id is None

    claimed = claim_next_run(db, "worker-two")
    assert claimed is not None
    assert str(claimed.id) == run_id
    assert claimed.worker_id == "worker-two"


def test_a_run_marked_not_retry_safe_is_not_silently_restarted(
    client: TestClient, db: Session
) -> None:
    require_database()
    from datetime import UTC, datetime, timedelta

    run_id = start_run(client, db, "Unsafe")
    db.execute(
        update(GenerationRun)
        .where(GenerationRun.id == uuid.UUID(run_id))
        .values(
            status="running",
            retry_safe=False,
            heartbeat_at=datetime.now(UTC) - timedelta(hours=1),
        )
    )
    db.commit()

    # Left alone on purpose: a human should decide, not the recovery sweep.
    assert recover_stale_runs(db) == 0
    assert db.get(GenerationRun, uuid.UUID(run_id)).status == "running"


def test_a_run_survives_api_restart_and_resumes_from_its_checkpoint(
    client: TestClient, db: Session
) -> None:
    require_database()
    """The API and worker are separate processes; the run lives in the database."""
    run_id = start_run(client, db, "Restart")

    row = db.get(GenerationRun, uuid.UUID(run_id))
    context = load_context(row)
    context.scope_result = {"domain": "Git", "scope": "s", "target_user": "u"}
    context.goals = [{"key": "g1", "title": "T", "outcome": "O", "prerequisite_goal_keys": []}]
    store_checkpoint(db, row.id, context)

    # A fresh process reads the checkpoint back and resumes from the right step.
    restored = load_context(db.get(GenerationRun, uuid.UUID(run_id)))
    assert restored.scope_result["domain"] == "Git"
    assert restored.completed_checkpoints() == ["scope", "goals"]

    # The resumed run completes. It must reuse the checkpointed scope rather
    # than re-deriving it, so the artifact's domain stays "Git" even though the
    # original request asked about Docker.
    append_event(db, row.id, "run.recovered", payload={"previous_worker": "dead"})
    store = DatabaseRunStore(row.id)
    provider = build_provider(db, row.project_id, None)
    outcome = asyncio.run(run_pipeline(restored, provider, store))
    finish_run(
        db,
        row.id,
        status=outcome.status,
        context=outcome.context,
        metrics=build_metrics(outcome.context, outcome.provider_calls, started=0.0),
    )

    assert outcome.status == "completed"
    assert outcome.context.artifact["domain"]["name"] == "Git"
    resumed_steps = [
        event.payload_json.get("step")
        for event in read_events(db, row.id)
        if event.event_type == "step.started"
    ]
    # Steps whose output was checkpointed are skipped individually, not sliced
    # off as a block: a block slice would re-run H30/H40 over the checkpointed
    # goals, producing a process set that disagrees with them.
    assert "H10" not in resumed_steps, "H10 must not re-run over checkpointed scope"
    assert "H30" not in resumed_steps, "H30 must not re-run over checkpointed goals"
    assert "H40" in resumed_steps, "the first unsatisfied step still has to run"
    # The validation tail always re-runs; it decides publishability.
    assert "H120" in resumed_steps
    assert "H130" in resumed_steps


def test_a_cancelled_run_stops_and_keeps_its_checkpoints(client: TestClient, db: Session) -> None:
    require_database()
    """Cancellation must not discard the work already checkpointed."""
    run_id = start_run(client, db, "Cancel Mid Run")
    row = db.get(GenerationRun, uuid.UUID(run_id))
    context = load_context(row)
    context.scope_result = {"domain": "Git", "scope": "s", "target_user": "u"}
    context.goals = [{"key": "g1", "title": "T", "outcome": "O", "prerequisite_goal_keys": []}]
    store_checkpoint(db, row.id, context)

    assert client.post(f"/api/v1/generation-runs/{run_id}/cancel").status_code == 200

    store = DatabaseRunStore(row.id)
    provider = build_provider(db, row.project_id, None)
    outcome = asyncio.run(run_pipeline(context, provider, store))

    assert outcome.status == "cancelled"
    assert outcome.context.scope_result is not None
    assert outcome.context.goals
    # A cancelled run is not asked for a candidate.
    assert outcome.context.artifact is None
