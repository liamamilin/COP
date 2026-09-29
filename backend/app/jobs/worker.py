"""Worker process.

Polls the database-backed queue, claims one run at a time, executes the Harness
pipeline, and writes progress events. The worker holds no in-memory state that
matters, so killing and restarting it is safe: a run whose heartbeat went cold
is requeued by `recover_stale_runs` and resumes from its last checkpoint.
"""

import asyncio
import logging
import os
import socket
import time
from typing import Any

from sqlalchemy import select

from app.core.config import get_settings
from app.core.errors import CopStudioError
from app.db.models import GenerationRun
from app.db.session import SessionLocal
from app.harness.provider_factory import build_provider
from app.harness.runner import build_metrics, run_pipeline
from app.jobs.events import append_event
from app.jobs.runner import (
    DatabaseRunStore,
    claim_next_run,
    finish_run,
    load_context,
    load_source_bundle,
    load_target_context,
    record_worker_heartbeat,
    recover_stale_runs,
)
from app.research import ExaSearchClient, enrich_context_with_web_search

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("cop.worker")
worker_id = f"{socket.gethostname()}:{os.getpid()}"

RECOVERY_INTERVAL_SECONDS = 60
HEARTBEAT_LOG_INTERVAL_SECONDS = 30

TERMINAL_EVENTS = {
    "completed": "run.completed",
    "cancelled": "run.cancelled",
    "needs_attention": "run.needs_attention",
    "failed": "run.failed",
}


def worker_heartbeat() -> None:
    with SessionLocal() as db:
        record_worker_heartbeat(db, worker_id)


def pending_run_id() -> Any:
    with SessionLocal() as db:
        return db.scalar(
            select(GenerationRun.id)
            .where(GenerationRun.status == "queued")
            .order_by(GenerationRun.created_at)
            .limit(1)
        )


def run_maintenance() -> None:
    """Heartbeat plus stale-run recovery."""
    worker_heartbeat()
    with SessionLocal() as db:
        recover_stale_runs(db)


async def execute_run() -> bool:
    """Claim and execute one run. Returns True when a run was actually claimed."""
    with SessionLocal() as db:
        run = claim_next_run(db, worker_id)
        if run is None:
            return False
        run_id = run.id
        context = load_context(run)
        # Database sources are reloaded on every attempt. Synthetic search
        # sources live in the checkpoint, so preserve them across crash
        # recovery instead of paying for the same query twice.
        persisted_search = [
            item for item in context.source_bundle if item.get("type") == "web_search"
        ]
        context.source_bundle = load_source_bundle(db, run) + persisted_search
        if context.input.get("web_search") and not context.partial_target:
            try:
                if not settings.exa_api_key:
                    raise CopStudioError(
                        "SEARCH_NOT_CONFIGURED",
                        "Web research was requested, but EXA_API_KEY is not configured.",
                        status_code=422,
                    )
                result_count = await enrich_context_with_web_search(
                    context,
                    ExaSearchClient(
                        api_key=settings.exa_api_key,
                        base_url=settings.exa_base_url,
                    ),
                    num_results=settings.exa_num_results,
                )
                append_event(
                    db,
                    run_id,
                    "research.search_completed",
                    payload={"provider": "exa", "result_count": result_count},
                )
            except CopStudioError as exc:
                append_event(
                    db,
                    run_id,
                    "run.failed",
                    payload={"code": exc.code, "message": exc.message},
                )
                finish_run(
                    db,
                    run_id,
                    status="failed",
                    context=context,
                    metrics={},
                    error_code=exc.code,
                    error_message=exc.message,
                )
                return True
        if context.partial_target and not load_target_context(db, run, context):
            # Nothing to refine. Fail with a reason the user can act on rather
            # than letting H140 crash on a missing artifact.
            message = "There is no draft or published version to refine yet."
            append_event(
                db,
                run_id,
                "run.failed",
                payload={"code": "REFINE_NO_BASE", "message": message},
            )
            finish_run(
                db,
                run_id,
                status="failed",
                context=context,
                metrics={},
                error_code="REFINE_NO_BASE",
                error_message=message,
            )
            return True
        try:
            provider = build_provider(db, run.project_id, context.input.get("settings_override"))
        except Exception as exc:  # noqa: BLE001 - configuration errors are user-facing
            code = getattr(exc, "code", "PROVIDER_NOT_CONFIGURED")
            append_event(db, run_id, "run.failed", payload={"code": code, "message": str(exc)})
            finish_run(
                db,
                run_id,
                status="failed",
                context=context,
                metrics={},
                error_code=code,
                error_message=str(exc),
            )
            return True

    started = time.monotonic()
    store = DatabaseRunStore(run_id)
    outcome = await run_pipeline(context, provider, store)
    metrics = build_metrics(outcome.context, outcome.provider_calls, started)

    with SessionLocal() as db:
        # The failing step's own code and message are surfaced, so the user sees
        # the real cause (a rate limit, a rejected key) rather than a generic
        # "generation failed".
        finish_run(
            db,
            run_id,
            status=outcome.status,
            context=outcome.context,
            metrics=metrics,
            error_code=outcome.error_code,
            error_message=outcome.error_message,
        )
        append_event(
            db,
            run_id,
            TERMINAL_EVENTS.get(outcome.status, "run.failed"),
            payload={
                "status": outcome.status,
                "code": outcome.error_code,
                "message": outcome.error_message,
                "metrics": {key: value for key, value in metrics.items() if key != "calls"},
            },
        )
    logger.info("run %s finished with status %s", run_id, outcome.status)
    return True


async def run_forever() -> None:
    logger.info("worker started id=%s", worker_id)
    last_recovery = 0.0
    last_heartbeat = 0.0
    while True:
        try:
            if time.monotonic() - last_recovery >= RECOVERY_INTERVAL_SECONDS:
                run_maintenance()
                last_recovery = time.monotonic()
            if time.monotonic() - last_heartbeat >= HEARTBEAT_LOG_INTERVAL_SECONDS:
                logger.info("worker heartbeat id=%s", worker_id)
                last_heartbeat = time.monotonic()
        except Exception:
            logger.exception("worker maintenance failed")

        try:
            if pending_run_id() is None:
                await asyncio.sleep(max(settings.worker_poll_seconds, 0.5))
                continue
            await execute_run()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("run execution failed")
            await asyncio.sleep(max(settings.worker_poll_seconds, 0.5))


def main() -> None:
    try:
        asyncio.run(run_forever())
    except KeyboardInterrupt:
        logger.info("worker stopped id=%s", worker_id)


if __name__ == "__main__":
    main()
