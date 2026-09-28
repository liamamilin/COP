"""Append-only generation event log.

Events are the transport for the SSE stream. The table has a unique
(run_id, sequence) constraint, so writers retry once on a concurrent insert to
keep progress streaming under parallel step execution.
"""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import GenerationEvent

BATCH_SIZE = 500


def next_sequence(db: Session, run_id: Any) -> int:
    current = db.scalar(
        select(func.coalesce(func.max(GenerationEvent.sequence), 0)).where(
            GenerationEvent.run_id == run_id
        )
    )
    return int(current or 0) + 1


def append_event(
    db: Session,
    run_id: Any,
    event_type: str,
    *,
    step: str | None = None,
    payload: dict[str, Any] | None = None,
    sequence: int | None = None,
) -> GenerationEvent | None:
    """Append one event, resolving the sequence automatically when omitted."""
    for _attempt in range(2):
        resolved = sequence if sequence is not None else next_sequence(db, run_id)
        statement = (
            insert(GenerationEvent)
            .values(
                run_id=run_id,
                sequence=resolved,
                event_type=event_type,
                step=step,
                payload_json=payload or {},
            )
            .on_conflict_do_nothing(index_elements=["run_id", "sequence"])
        )
        db.execute(statement)
        db.commit()
        event = db.scalar(
            select(GenerationEvent).where(
                GenerationEvent.run_id == run_id, GenerationEvent.sequence == resolved
            )
        )
        if event is not None:
            return event
        db.rollback()
    return None


def append_events(
    db: Session, run_id: Any, events: list[tuple[str, str | None, dict[str, Any]]]
) -> int:
    """Append a batch of (event_type, step, payload) tuples."""
    written = 0
    for event_type, step, payload in events:
        if append_event(db, run_id, event_type, step=step, payload=payload) is not None:
            written += 1
    return written


def read_events(
    db: Session, run_id: Any, *, after: int = 0, limit: int = BATCH_SIZE
) -> list[GenerationEvent]:
    return list(
        db.scalars(
            select(GenerationEvent)
            .where(GenerationEvent.run_id == run_id, GenerationEvent.sequence > after)
            .order_by(GenerationEvent.sequence)
            .limit(limit)
        )
    )


def safe_append(db: Session, run_id: Any, event_type: str, payload: dict[str, Any]) -> None:
    """Append without raising. Event logging must never fail a run."""
    try:
        append_event(db, run_id, event_type, payload=payload)
    except IntegrityError:
        db.rollback()
    except Exception:  # noqa: BLE001 - progress is best-effort
        db.rollback()
