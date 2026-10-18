"""Generation run API.

Endpoints per the API contract:

- `POST /projects/{project_id}/generation-runs`  start a run
- `GET  /generation-runs/{run_id}`               status
- `GET  /generation-runs/{run_id}/events`        SSE progress stream
- `POST /generation-runs/{run_id}/cancel`        request cancellation
"""

import asyncio
import json
import uuid
from collections.abc import AsyncIterator
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import CopStudioError, NotFoundError
from app.db.models import COPVersion, GenerationRun, Project
from app.db.session import SessionLocal, get_db
from app.domain.patches import REFINABLE_ENTITIES
from app.harness.provider_factory import resolve_effective_settings_with_run
from app.harness.steps import PHASES, TARGETED_PHASES
from app.jobs.events import read_events
from app.jobs.runner import (
    create_run,
    latest_sequence,
    run_events_payload,
    set_cancelled,
)

router = APIRouter(tags=["generation"])
DbSession = Annotated[Session, Depends(get_db)]

TERMINAL_STATUSES = {"completed", "needs_attention", "failed", "cancelled"}
SSE_POLL_SECONDS = 0.4
SSE_KEEPALIVE_SECONDS = 15.0


class TargetSelection(BaseModel):
    entity_type: Literal["goal", "process", "stage"]
    entity_id: str = Field(min_length=1, max_length=180)


@router.get("/projects/{project_id}/generation-settings")
def get_effective_generation_settings(
    project_id: uuid.UUID, db: DbSession, run: str | None = None
) -> dict[str, Any]:
    """The generation settings a run on this project would use right now.

    The browser calls this instead of merging anything itself. Spec `24` §8 puts
    the merge in the backend, and a second implementation of precedence in the
    client is a second thing that can drift from what actually runs.

    `?run=` carries a JSON-encoded `settings_override` so the panel can preview
    the exact values a particular run would receive before starting it.
    """
    if db.get(Project, project_id) is None:
        raise NotFoundError("Project not found", code="PROJECT_NOT_FOUND")
    override: dict[str, Any] | None = None
    if run:
        try:
            decoded = json.loads(run)
        except json.JSONDecodeError as exc:
            raise CopStudioError(
                "INVALID_SETTINGS_OVERRIDE",
                "The 'run' query parameter must be a JSON object.",
                status_code=422,
            ) from exc
        if not isinstance(decoded, dict):
            raise CopStudioError(
                "INVALID_SETTINGS_OVERRIDE",
                "The 'run' query parameter must be a JSON object.",
                status_code=422,
            )
        override = decoded
    effective = resolve_effective_settings_with_run(db, project_id, override)
    generation = effective.get("generation") or {}
    # `harness_view` is the flattened form the worker actually reads. Exposing it
    # makes "the UI shows X, the Harness read Y" checkable without a debugger.
    return {"effective": generation, "harness_view": {**effective, **generation}}


class GenerationRunCreate(BaseModel):
    mode: Literal["fast", "standard", "deep"] = "standard"
    topic: str = Field(default="", max_length=400)
    scope_hint: str = Field(default="", max_length=2000)
    target_outcomes: list[str] = Field(default_factory=list, max_length=12)
    learner_level: Literal["new", "some_experience", "advanced"] = "new"
    source_ids: list[uuid.UUID] = Field(default_factory=list, max_length=50)
    web_search: bool = False
    settings_override: dict[str, Any] = Field(default_factory=dict)
    base_version_id: uuid.UUID | None = None
    target: TargetSelection | None = None
    instruction: str = Field(default="", max_length=2000)


class GenerationRunOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    status: str
    requested_mode: str
    base_version_id: uuid.UUID | None
    started_at: Any = None
    completed_at: Any = None
    heartbeat_at: Any = None
    worker_id: str | None
    cancel_requested: bool
    error_code: str | None
    error_message: str | None
    metrics: dict[str, Any]
    created_at: Any = None
    updated_at: Any = None


class PhaseOut(BaseModel):
    key: str
    label: str
    steps: list[str]
    status: Literal["pending", "active", "done"]


def _require_project(db: Session, project_id: uuid.UUID) -> Project:
    # Shared with the draft API so a missing project produces one identical 404
    # envelope rather than a bare FastAPI detail string.
    from app.api.drafts import require_project

    return require_project(db, project_id)


def _require_run(db: Session, run_id: uuid.UUID) -> GenerationRun:
    run = db.get(GenerationRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Generation run not found")
    return run


def run_out(run: GenerationRun) -> GenerationRunOut:
    return GenerationRunOut(
        id=run.id,
        project_id=run.project_id,
        status=run.status,
        requested_mode=run.requested_mode,
        base_version_id=run.base_version_id,
        started_at=run.started_at,
        completed_at=run.completed_at,
        heartbeat_at=run.heartbeat_at,
        worker_id=run.worker_id,
        cancel_requested=run.cancel_requested,
        error_code=run.error_code,
        error_message=run.error_message,
        metrics=dict(run.metrics_json or {}),
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


def _is_targeted(events: list[dict[str, Any]]) -> bool:
    """True when the event log shows the short refinement pipeline.

    Detected from H140 rather than from the run row, because `phase_states` only
    has the events. A refinement that never reached H140 reports the full list,
    which is the honest answer: it failed before proposing anything.
    """
    return any(event.get("step") == "H140" for event in events)


def phase_states(events: list[dict[str, Any]], *, run_status: str) -> list[PhaseOut]:
    """Derive per-phase progress from the event log.

    A targeted run reports the two phases it actually has, rather than the ten a
    full generation walks through. Showing an untouched ten-item list for a
    refinement would imply far more work than is happening.
    """
    source = TARGETED_PHASES if _is_targeted(events) else PHASES
    step_to_phase = {step: key for key, _label, steps in source for step in steps}
    completed_steps: set[str] = set()
    active_steps: set[str] = set()
    for event in events:
        step = event.get("step")
        if not step or str(step) not in step_to_phase:
            continue
        if event["type"] == "step.started":
            active_steps.add(str(step))
        elif event["type"] == "step.completed":
            completed_steps.add(str(step))
            active_steps.discard(str(step))

    terminal = run_status in TERMINAL_STATUSES
    states: list[PhaseOut] = []
    for key, label, steps in source:
        phase_steps = set(steps)
        if phase_steps <= completed_steps:
            state = "done"
        elif phase_steps & active_steps:
            state = "active"
        elif terminal:
            state = "pending"
        else:
            state = "pending"
        states.append(PhaseOut(key=key, label=label, steps=list(steps), status=state))
    return states


@router.post(
    "/projects/{project_id}/generation-runs",
    response_model=GenerationRunOut,
    status_code=status.HTTP_201_CREATED,
)
def start_generation_run(
    project_id: uuid.UUID, body: GenerationRunCreate, db: DbSession
) -> GenerationRunOut:
    _require_project(db, project_id)
    if body.target is not None:
        # A targeted run refines something that already exists, so it must not
        # demand a topic. Validating the target here gives the user a real error
        # at request time rather than a failed run minutes later.
        if body.target.entity_type not in REFINABLE_ENTITIES:
            raise CopStudioError(
                "TARGET_NOT_REFINABLE",
                f"'{body.target.entity_type}' cannot be refined. Refinable types are: "
                f"{', '.join(REFINABLE_ENTITIES)}",
                status_code=422,
            )
    elif not body.topic.strip() and not body.source_ids:
        raise CopStudioError(
            "HARNESS_INTAKE_INCOMPLETE",
            "Provide a topic or attach at least one source before running the Harness",
            status_code=422,
        )
    if body.base_version_id is not None:
        base = db.get(COPVersion, body.base_version_id)
        if base is None or base.project_id != project_id:
            raise NotFoundError("Base version not found in this project", code="VERSION_NOT_FOUND")

    effective = resolve_effective_settings_with_run(db, project_id, body.settings_override)
    requested_input = {
        "topic": body.topic,
        "scope_hint": body.scope_hint,
        "target_outcomes": body.target_outcomes,
        "learner_level": body.learner_level,
        "source_ids": [str(item) for item in body.source_ids],
        "web_search": body.web_search,
        "settings_override": body.settings_override,
        "target": body.target.model_dump() if body.target else None,
        "instruction": body.instruction,
    }
    run = create_run(
        db,
        project_id=project_id,
        mode=body.mode,
        requested_input=requested_input,
        # Flattened here, at the point where the effective settings are known,
        # rather than only inside the worker. A run row that records the nested
        # request-shaped form cannot answer "which settings did this run use",
        # and the worker may not run for a long time or at all.
        settings={**effective, **(effective.get("generation") or {})},
        base_version_id=body.base_version_id,
    )
    return run_out(run)


@router.get("/projects/{project_id}/generation-runs", response_model=list[GenerationRunOut])
def list_generation_runs(
    project_id: uuid.UUID, db: DbSession, limit: int = 20
) -> list[GenerationRunOut]:
    _require_project(db, project_id)
    runs = db.scalars(
        select(GenerationRun)
        .where(GenerationRun.project_id == project_id)
        .order_by(GenerationRun.created_at.desc())
        .limit(max(1, min(limit, 100)))
    )
    return [run_out(run) for run in runs]


@router.get("/generation-runs/{run_id}", response_model=GenerationRunOut)
def get_generation_run(run_id: uuid.UUID, db: DbSession) -> GenerationRunOut:
    return run_out(_require_run(db, run_id))


@router.get("/generation-runs/{run_id}/events")
def stream_generation_events(
    run_id: uuid.UUID, request: Request, db: DbSession, last_event_id: int | None = None
) -> StreamingResponse:
    """Server-Sent Events stream of run progress.

    Historical events are replayed first (honouring `Last-Event-ID` so a browser
    reconnect resumes instead of restarting), then the stream polls for new
    rows and closes once the run reaches a terminal state.
    """
    _require_run(db, run_id)
    db.close()

    async def publisher() -> AsyncIterator[bytes]:
        cursor = last_event_id or 0
        header = request.headers.get("last-event-id")
        if header and header.isdigit():
            cursor = int(header)
        idle = 0
        while True:
            if await request.is_disconnected():
                return
            with SessionLocal() as stream_db:
                events = read_events(stream_db, run_id, after=cursor)
            for event in events:
                cursor = event.sequence
                yield _sse(
                    event.event_type,
                    {"sequence": event.sequence, "step": event.step, **event.payload_json},
                    event_id=event.sequence,
                )
            if events:
                idle = 0
            else:
                # A comment line keeps proxies from closing an idle stream.
                yield b": keepalive\n\n"
                idle += 1
                if idle >= int(SSE_KEEPALIVE_SECONDS / SSE_POLL_SECONDS):
                    idle = 0
            if _is_terminal(cursor, run_id):
                return
            await asyncio.sleep(SSE_POLL_SECONDS)

    return StreamingResponse(
        publisher(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _is_terminal(cursor: int, run_id: uuid.UUID) -> bool:
    with SessionLocal() as db:
        run = db.get(GenerationRun, run_id)
        if run is None or run.status not in TERMINAL_STATUSES:
            return False
        # Close only after the terminal event itself has been sent.
        return latest_sequence(db, run_id) <= cursor


def _sse(event_type: str, data: dict[str, Any], *, event_id: int | None = None) -> bytes:
    prefix = f"id: {event_id}\n" if event_id is not None else ""
    return f"{prefix}event: {event_type}\ndata: {json.dumps(data, default=str)}\n\n".encode()


@router.post("/generation-runs/{run_id}/cancel", response_model=GenerationRunOut)
def cancel_generation_run(run_id: uuid.UUID, db: DbSession) -> GenerationRunOut:
    run = _require_run(db, run_id)
    if run.status in TERMINAL_STATUSES:
        raise CopStudioError(
            "GENERATION_ALREADY_TERMINAL",
            f"Run already finished with status '{run.status}'",
            status_code=409,
        )
    set_cancelled(db, run_id)
    db.refresh(run)
    return run_out(run)


@router.get("/generation-runs/{run_id}/progress")
def generation_progress(run_id: uuid.UUID, db: DbSession) -> dict[str, Any]:
    """Polling fallback for clients that cannot hold an SSE connection."""
    run = _require_run(db, run_id)
    events = run_events_payload(db, run_id)
    return {
        "run": run_out(run).model_dump(mode="json"),
        "phases": [phase.model_dump() for phase in phase_states(events, run_status=run.status)],
        "candidate_available": run.candidate_artifact_json is not None,
    }


@router.get("/generation-runs/{run_id}/candidate")
def candidate_artifact(run_id: uuid.UUID, db: DbSession) -> dict[str, Any]:
    run = _require_run(db, run_id)
    if run.candidate_artifact_json is None:
        raise CopStudioError(
            "CANDIDATE_NOT_READY",
            "This run has not produced a candidate artifact yet",
            status_code=409,
        )
    return {
        "run_id": str(run.id),
        "status": run.status,
        "artifact": run.candidate_artifact_json,
        "warnings": (run.metrics_json or {}).get("warnings", []),
    }
