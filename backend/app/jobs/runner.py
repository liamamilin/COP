"""Database-backed job runner.

Implements the `RunStore` the Harness needs, plus the claim/recovery protocol
from the architecture doc:

1. poll queued jobs,
2. claim the oldest one inside a transaction using `FOR UPDATE SKIP LOCKED`,
3. mark it running and record the worker id,
4. execute, heartbeating as it goes,
5. requeue stale running jobs so a crashed worker does not strand a run.

`SKIP LOCKED` is what lets several workers share the queue without blocking each
other or double-claiming a run.
"""

import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import cast, func, select, update
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.orm import Session

from app.db.models import (
    AppSetting,
    COPVersion,
    Draft,
    GenerationEvent,
    GenerationRun,
    Project,
    Source,
    SourceDocument,
)
from app.db.session import SessionLocal
from app.harness.context import HarnessContext, HarnessEvent
from app.harness.steps.h00_intake import MAX_SOURCE_EXCERPT
from app.jobs.events import append_event, read_events

logger = logging.getLogger("cop.jobs")

STALE_AFTER_SECONDS = 300
CLAIM_BATCH = 5


def now() -> datetime:
    return datetime.now(UTC)


def claim_next_run(db: Session, worker_id: str) -> GenerationRun | None:
    """Claim the oldest queued run for this worker, or return None."""
    candidate = db.scalar(
        select(GenerationRun.id)
        .where(GenerationRun.status == "queued")
        .order_by(GenerationRun.created_at)
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    if candidate is None:
        return None
    result = db.execute(
        update(GenerationRun)
        .where(GenerationRun.id == candidate, GenerationRun.status == "queued")
        .values(
            status="running",
            worker_id=worker_id,
            started_at=now(),
            heartbeat_at=now(),
            updated_at=now(),
        )
    )
    db.commit()
    if result.rowcount == 0:
        return None
    return db.get(GenerationRun, candidate)


def recover_stale_runs(db: Session, *, older_than_seconds: int = STALE_AFTER_SECONDS) -> int:
    """Requeue running jobs whose heartbeat went cold.

    Only retry-safe runs are requeued. A run marked not retry-safe is left for a
    human to inspect rather than silently restarted.
    """
    threshold = now() - timedelta(seconds=older_than_seconds)
    stale = list(
        db.scalars(
            select(GenerationRun).where(
                GenerationRun.status == "running",
                GenerationRun.retry_safe.is_(True),
                GenerationRun.heartbeat_at.is_not(None),
                GenerationRun.heartbeat_at < threshold,
            )
        )
    )
    for run in stale:
        append_event(
            db,
            run.id,
            "run.recovered",
            payload={"previous_worker": run.worker_id, "status": "queued"},
        )
    if stale:
        db.execute(
            update(GenerationRun)
            .where(GenerationRun.id.in_([run.id for run in stale]))
            .values(status="queued", worker_id=None, started_at=None, updated_at=now())
        )
        db.commit()
        logger.warning("Recovered %d stale generation run(s)", len(stale))
    return len(stale)


def set_cancelled(db: Session, run_id: Any) -> bool:
    """Flag a run for cancellation. Returns False when already terminal."""
    result = db.execute(
        update(GenerationRun)
        .where(GenerationRun.id == run_id, GenerationRun.status.in_(["queued", "running"]))
        .values(cancel_requested=True, updated_at=now())
    )
    db.commit()
    if result.rowcount == 0:
        return False
    append_event(db, run_id, "run.cancelling", payload={})
    return True


def load_context(run: GenerationRun) -> HarnessContext:
    checkpoint = run.checkpoint_json or {}
    context = (
        HarnessContext.from_dict(checkpoint)
        if checkpoint
        else HarnessContext(run_id=str(run.id), project_id=str(run.project_id))
    )
    context.run_id = str(run.id)
    context.project_id = str(run.project_id)
    context.base_version_id = str(run.base_version_id) if run.base_version_id else None
    context.input = context.input or run.requested_sections_json or {}
    context.settings = context.settings or run.model_config_json or {}
    # The API accepted `target` from the start but nothing ever read it, so a
    # targeted run silently produced a whole new COP. Routing on it here is what
    # makes `target` mean anything.
    target = context.input.get("target")
    context.partial_target = dict(target) if isinstance(target, dict) and target else None
    return context


def load_source_bundle(db: Session, run: GenerationRun) -> list[dict[str, Any]]:
    """Fetch the source text the run should read, capped per source."""
    requested = list((run.requested_sections_json or {}).get("source_ids") or [])
    statement = (
        select(Source, SourceDocument)
        .outerjoin(SourceDocument, SourceDocument.source_id == Source.id)
        .where(Source.project_id == run.project_id)
    )
    if requested:
        statement = statement.where(Source.id.in_(requested))
    bundle: list[dict[str, Any]] = []
    for source, document in db.execute(statement).all():
        bundle.append(
            {
                "id": str(source.id),
                "title": source.title,
                "type": source.type,
                "status": source.status,
                "text": (document.text or "")[:MAX_SOURCE_EXCERPT] if document else "",
            }
        )
    return bundle


def run_events_payload(db: Session, run_id: Any) -> list[dict[str, Any]]:
    return [
        {
            "sequence": event.sequence,
            "type": event.event_type,
            "step": event.step,
            "payload": event.payload_json,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
        for event in read_events(db, run_id)
    ]


def latest_sequence(db: Session, run_id: Any) -> int:
    value = db.scalar(
        select(func.coalesce(func.max(GenerationEvent.sequence), 0)).where(
            GenerationEvent.run_id == run_id
        )
    )
    return int(value or 0)


def record_worker_heartbeat(db: Session, worker_id: str) -> None:
    """Publish worker liveness into the single app_settings row."""
    payload = {"worker_id": worker_id, "heartbeat_at": now().isoformat()}
    statement = insert(AppSetting).values(id=1, settings_json={"worker": payload})
    statement = statement.on_conflict_do_update(
        index_elements=[AppSetting.id],
        set_={
            "settings_json": AppSetting.settings_json.op("||")(cast({"worker": payload}, JSONB)),
            "updated_at": now(),
        },
    )
    db.execute(statement)
    db.commit()


def create_run(
    db: Session,
    *,
    project_id: Any,
    mode: str,
    requested_input: dict[str, Any],
    settings: dict[str, Any],
    base_version_id: Any = None,
) -> GenerationRun:
    run = GenerationRun(
        project_id=project_id,
        base_version_id=base_version_id,
        status="queued",
        requested_mode=mode,
        requested_sections_json=requested_input,
        model_config_json=settings,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    append_event(db, run.id, "run.queued", payload={"mode": mode})
    return run


def project_for_run(db: Session, run: GenerationRun) -> Project | None:
    return db.get(Project, run.project_id)


def store_checkpoint(db: Session, run_id: Any, context: HarnessContext) -> None:
    db.execute(
        update(GenerationRun)
        .where(GenerationRun.id == run_id)
        .values(
            checkpoint_json=json.loads(context.to_json()),
            heartbeat_at=now(),
            updated_at=now(),
        )
    )
    db.commit()


def load_target_context(db: Session, run: GenerationRun, context: HarnessContext) -> bool:
    """Point a targeted run at the artifact it should refine.

    Preference order matters: an active draft is what the user is looking at and
    what accepting will write back to, so it wins over the published version. A
    refinement proposed against stale published content would show a before/after
    that does not match the screen it was launched from.

    Returns False when there is nothing to refine, so the caller can fail the run
    with a real reason instead of letting H140 crash on a missing artifact.
    """
    draft = db.scalar(select(Draft).where(Draft.project_id == run.project_id))
    if draft is not None:
        context.artifact = draft.artifact_json
        context.locked_paths = list(draft.locked_paths or [])
        return True
    if run.base_version_id:
        version = db.get(COPVersion, run.base_version_id)
        if version is not None:
            context.artifact = version.artifact_json
            return True
    return False


def finish_run(
    db: Session,
    run_id: Any,
    *,
    status: str,
    context: HarnessContext,
    metrics: dict[str, Any],
    error_code: str | None = None,
    error_message: str | None = None,
) -> None:
    values: dict[str, Any] = {
        "status": status,
        "candidate_artifact_json": context.artifact,
        "checkpoint_json": json.loads(context.to_json()),
        "metrics_json": metrics,
        "completed_at": now(),
        "error_code": error_code,
        "error_message": error_message,
        "updated_at": now(),
    }
    # A targeted run's proposal is its result. `ready` is only claimed once the
    # patch actually exists, so a failed refinement never shows an empty
    # preview as though it had produced something.
    if context.candidate_patch is not None:
        values["candidate_patch_json"] = context.candidate_patch
        values["patch_state"] = "ready"
    db.execute(update(GenerationRun).where(GenerationRun.id == run_id).values(**values))
    db.commit()


def emit_harness_event(db: Session, run_id: Any, event: HarnessEvent) -> None:
    """Persist one Harness event.

    The step goes in the dedicated `step` column rather than only the payload,
    so the progress endpoint can group events by step without unpacking JSON
    for every row.
    """
    step = event.payload.get("step")
    try:
        append_event(
            db,
            run_id,
            event.event_type,
            step=str(step) if step else None,
            payload=event.payload,
        )
    except Exception:  # noqa: BLE001 - progress must never fail the run
        db.rollback()
        logger.warning("Failed to append %s event for run %s", event.event_type, run_id)


class DatabaseRunStore:
    """`RunStore` implementation bound to one database session per operation."""

    def __init__(self, run_id: Any) -> None:
        self.run_id = run_id

    def emit(self, run_id: Any, events: list[HarnessEvent]) -> None:
        with SessionLocal() as db:
            for event in events:
                emit_harness_event(db, run_id, event)

    def save_checkpoint(self, run_id: Any, context: HarnessContext) -> None:
        with SessionLocal() as db:
            store_checkpoint(db, run_id, context)

    def heartbeat(self, run_id: Any) -> None:
        with SessionLocal() as db:
            db.execute(
                update(GenerationRun)
                .where(GenerationRun.id == run_id)
                .values(heartbeat_at=now(), updated_at=now())
            )
            db.commit()

    def metrics(self, run_id: Any) -> dict[str, Any]:
        with SessionLocal() as db:
            run = db.get(GenerationRun, run_id)
            return dict(run.metrics_json or {}) if run else {}

    def is_cancelled(self, run_id: Any) -> bool:
        with SessionLocal() as db:
            run = db.get(GenerationRun, run_id)
            return bool(run and run.cancel_requested)

    def set_candidate(self, run_id: Any, artifact: dict[str, Any] | None) -> None:
        with SessionLocal() as db:
            db.execute(
                update(GenerationRun)
                .where(GenerationRun.id == run_id)
                .values(candidate_artifact_json=artifact, updated_at=now())
            )
            db.commit()
