"""Resume transaction and read model. The event log is the attempt history."""

import copy
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import CopStudioError, NotFoundError
from app.db.models import GenerationEvent, GenerationRun, Project
from app.harness.recovery import recovery_plan
from app.jobs.events import next_sequence
from app.jobs.runner import now

RESUME_EVENT = "run.resume_requested"


def resume_events(db: Session, run_id: Any) -> list[GenerationEvent]:
    return list(
        db.scalars(
            select(GenerationEvent)
            .where(
                GenerationEvent.run_id == run_id,
                GenerationEvent.event_type == RESUME_EVENT,
            )
            .order_by(GenerationEvent.sequence)
        )
    )


def recovery_view(db: Session, run: GenerationRun) -> dict[str, Any]:
    events = resume_events(db, run.id)
    plan = recovery_plan(
        status=run.status,
        retry_safe=run.retry_safe,
        targeted=bool((run.requested_sections_json or {}).get("target")),
        error_code=run.error_code,
        checkpoint=run.checkpoint_json or {},
    )
    provider = (run.model_config_json or {}).get("provider") or {}
    if plan.allowed and (
        not provider.get("type")
        or (
            provider.get("type") != "mock"
            and not all(provider.get(k) for k in ("base_url", "model"))
        )
    ):
        return {
            "allowed": False,
            "reason": "The original model configuration is missing. Start over to continue.",
            "attempt": len(events) + 1,
            "event_cursor": events[-1].sequence if events else 0,
            "from_step": None,
            "completed_steps": [],
            "timeout_seconds": 60,
            "history": [e.payload_json["previous_attempt"] for e in events],
        }
    return {
        "allowed": plan.allowed,
        "reason": plan.reason,
        "from_step": plan.from_step,
        "completed_steps": list(plan.completed_steps),
        "attempt": len(events) + 1,
        "event_cursor": events[-1].sequence if events else 0,
        "timeout_seconds": provider.get("timeout") or 60,
        "history": [e.payload_json["previous_attempt"] for e in events],
    }


def resume_run(
    db: Session,
    run_id: Any,
    *,
    expected_attempt: int,
    timeout_seconds: int | None = None,
) -> GenerationRun:
    # Row lock plus expected_attempt makes duplicate clicks/retries harmless,
    # even if the new attempt has already failed before an old request arrives.
    run = db.scalar(
        select(GenerationRun)
        .where(GenerationRun.id == run_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if run is None:
        raise NotFoundError("Generation run not found", code="GENERATION_RUN_NOT_FOUND")
    project = db.get(Project, run.project_id)
    if project is None or project.status != "active":
        raise CopStudioError("RESUME_NOT_ALLOWED", "The project is not active.", status_code=409)
    view = recovery_view(db, run)
    if expected_attempt < view["attempt"]:
        db.rollback()
        return run
    if expected_attempt != view["attempt"] or not view["allowed"]:
        raise CopStudioError(
            "RESUME_NOT_ALLOWED",
            view["reason"] or "This run has changed. Refresh to continue.",
            status_code=409,
        )

    checkpoint = copy.deepcopy(run.checkpoint_json)
    model_config = copy.deepcopy(run.model_config_json)
    previous = {
        "attempt": view["attempt"],
        "status": run.status,
        "error_code": run.error_code,
        "error_message": run.error_message,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "metrics": run.metrics_json or {},
        "timeout_seconds": view["timeout_seconds"],
    }
    if timeout_seconds is not None:
        model_config["provider"]["timeout"] = timeout_seconds
        checkpoint["settings"]["provider"] = copy.deepcopy(model_config["provider"])
    boundary = next_sequence(db, run.id)
    # History and queue transition commit atomically. Do not use append_event,
    # which commits independently and would release the lock too soon.
    db.add(
        GenerationEvent(
            run_id=run.id,
            sequence=boundary,
            event_type=RESUME_EVENT,
            payload_json={
                "from_step": view["from_step"],
                "completed_steps": view["completed_steps"],
                "attempt": view["attempt"] + 1,
                "previous_attempt": previous,
            },
        )
    )
    run.status = "queued"
    run.cancel_requested = False
    run.worker_id = None
    run.started_at = None
    run.completed_at = None
    run.heartbeat_at = None
    run.error_code = None
    run.error_message = None
    run.candidate_artifact_json = None
    run.metrics_json = {}
    run.checkpoint_json = checkpoint
    run.model_config_json = model_config
    run.updated_at = now()
    db.commit()
    db.refresh(run)
    return run
