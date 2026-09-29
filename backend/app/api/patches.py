"""Candidate patch API.

Endpoints per `10-api-contracts.md` §6:

- `GET  /generation-runs/{run_id}/candidate-patch`   before/after preview
- `POST /generation-runs/{run_id}/candidate-patch/accept`
- `POST /generation-runs/{run_id}/candidate-patch/reject`

The state machine is `16-state-machines.md` §5: generating → ready → accepted |
rejected | expired. Only `accept` writes, and only ever to the active Draft. A
published version has no path from this router at all.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import CopStudioError, NotFoundError
from app.db.models import Draft, GenerationRun
from app.db.session import get_db
from app.domain.patches import apply_patch, patch_is_stale
from app.harness.steps.h120_validate import resolve_schema_path

router = APIRouter(tags=["patches"])
DbSession = Annotated[Session, Depends(get_db)]

# A patch is a proposal about one entity, so it expires rather than lingering:
# the longer it sits, the more likely the draft has moved on and the preview has
# stopped describing the screen it was launched from.
PATCH_TTL_SECONDS = 30 * 60


class PatchChange(BaseModel):
    field: str
    before: str
    after: str


class RejectedProposal(BaseModel):
    field: str
    reason: str
    value: str = ""


class CandidatePatchOut(BaseModel):
    run_id: uuid.UUID
    state: str
    project_id: uuid.UUID
    entity_type: str
    entity_id: str
    entity_title: str
    changes: list[PatchChange]
    rejected: list[RejectedProposal]
    locked_paths: list[str] = Field(default_factory=list)
    stale: bool = False


class PatchResult(BaseModel):
    state: str
    draft_id: uuid.UUID | None = None
    applied_fields: list[str] = Field(default_factory=list)
    skipped: list[RejectedProposal] = Field(default_factory=list)
    message: str


def _require_run(db: Session, run_id: uuid.UUID) -> GenerationRun:
    run = db.get(GenerationRun, run_id)
    if run is None:
        raise NotFoundError("Generation run not found", code="RUN_NOT_FOUND")
    return run


def _require_draft(db: Session, project_id: uuid.UUID) -> Draft:
    draft = db.scalar(select(Draft).where(Draft.project_id == project_id))
    if draft is None:
        raise CopStudioError(
            "NO_ACTIVE_DRAFT",
            "Accepting a refinement changes the active draft, and this project has "
            "none. Open the published version as a draft first.",
            status_code=409,
        )
    return draft


def _expired(run: GenerationRun) -> bool:
    from datetime import UTC, datetime, timedelta

    if run.completed_at is None:
        return False
    return datetime.now(UTC) - run.completed_at > timedelta(seconds=PATCH_TTL_SECONDS)


@router.get("/generation-runs/{run_id}/candidate-patch", response_model=CandidatePatchOut)
def get_candidate_patch(run_id: uuid.UUID, db: DbSession) -> CandidatePatchOut:
    """The before/after preview. Reading a patch never changes anything."""
    run = _require_run(db, run_id)
    if not run.candidate_patch_json:
        raise CopStudioError(
            "PATCH_NOT_READY",
            "This run has not produced a refinement proposal.",
            status_code=409,
            details={"state": run.patch_state},
        )

    patch = dict(run.candidate_patch_json)
    draft = db.scalar(select(Draft).where(Draft.project_id == run.project_id))
    return CandidatePatchOut(
        run_id=run.id,
        state="expired" if _expired(run) else run.patch_state,
        project_id=run.project_id,
        entity_type=str(patch.get("entity_type", "")),
        entity_id=str(patch.get("entity_id", "")),
        entity_title=str(patch.get("entity_title", "")),
        changes=[
            PatchChange(
                field=str(item.get("field", "")),
                before=str(item.get("before", "")),
                after=str(item.get("after", "")),
            )
            for item in patch.get("changes") or []
        ],
        rejected=[
            RejectedProposal(
                field=str(item.get("field", "")),
                reason=str(item.get("reason", "")),
                value=str(item.get("value", "")),
            )
            for item in patch.get("rejected") or []
        ],
        locked_paths=list(draft.locked_paths or []) if draft else [],
        # A stale patch still renders, but flagged: the user must not accept a
        # diff whose "before" no longer matches what is on screen.
        stale=bool(draft and patch_is_stale(patch, draft.artifact_json)),
    )


@router.post("/generation-runs/{run_id}/candidate-patch/accept", response_model=PatchResult)
def accept_candidate_patch(run_id: uuid.UUID, db: DbSession) -> PatchResult:
    """Apply the patch to the active draft. Never to a published version."""
    run = _require_run(db, run_id)
    if run.patch_state != "ready" or not run.candidate_patch_json:
        raise CopStudioError(
            "PATCH_NOT_ACCEPTABLE",
            f"This proposal is '{run.patch_state}' and cannot be accepted.",
            status_code=409,
            details={"state": run.patch_state},
        )
    if _expired(run):
        run.patch_state = "expired"
        db.commit()
        raise CopStudioError(
            "PATCH_EXPIRED",
            "This proposal is too old to apply safely. Run the refinement again.",
            status_code=409,
        )

    draft = _require_draft(db, run.project_id)
    patch = dict(run.candidate_patch_json)

    if patch_is_stale(patch, draft.artifact_json):
        run.patch_state = "expired"
        db.commit()
        raise CopStudioError(
            "PATCH_STALE",
            "The draft changed since this proposal was made, so applying it would "
            "discard your newer edit. Run the refinement again.",
            status_code=409,
        )

    # Re-check the locks at accept time. A field locked between proposing and
    # accepting must still be protected: the user may have edited it while the
    # preview was on screen.
    locked = set(draft.locked_paths or [])
    changes = []
    skipped: list[RejectedProposal] = []
    for change in patch.get("changes") or []:
        field = str(change.get("field", ""))
        entity_id = str(patch.get("entity_id", ""))
        if entity_id in locked or f"{entity_id}.{field}" in locked:
            skipped.append(
                RejectedProposal(
                    field=field,
                    reason="you edited this field by hand, so it is locked",
                    value=str(change.get("after", "")),
                )
            )
            continue
        changes.append(change)

    if not changes:
        run.patch_state = "expired"
        db.commit()
        return PatchResult(
            state=run.patch_state,
            draft_id=draft.id,
            skipped=skipped,
            message="Nothing to apply: every proposed field is one you have edited.",
        )

    updated = apply_patch(draft.artifact_json, {**patch, "changes": changes})
    try:
        from app.domain.validation import validate_artifact

        validate_artifact(updated, resolve_schema_path())
    except Exception as exc:  # noqa: BLE001
        raise CopStudioError(
            "PATCH_INVALID",
            f"Accepting this proposal would make the draft invalid, so it was refused: {exc}",
            status_code=422,
            details={"reason": str(exc)},
        ) from exc

    draft.artifact_json = updated
    run.patch_state = "accepted"
    db.commit()
    return PatchResult(
        state="accepted",
        draft_id=draft.id,
        applied_fields=[str(item.get("field")) for item in changes],
        skipped=skipped,
        message=(
            f"Applied {len(changes)} change(s) to the draft. The published version is unchanged."
        ),
    )


@router.post("/generation-runs/{run_id}/candidate-patch/reject", response_model=PatchResult)
def reject_candidate_patch(run_id: uuid.UUID, db: DbSession) -> PatchResult:
    """Discard the proposal. Must change nothing at all."""
    run = _require_run(db, run_id)
    if run.patch_state in {"accepted", "rejected"}:
        raise CopStudioError(
            "PATCH_ALREADY_DECIDED",
            f"This proposal was already {run.patch_state}.",
            status_code=409,
            details={"state": run.patch_state},
        )
    if run.patch_state != "ready" or not run.candidate_patch_json:
        raise CopStudioError(
            "PATCH_NOT_REJECTABLE",
            f"This proposal is '{run.patch_state}' and is not ready for a decision.",
            status_code=409,
            details={"state": run.patch_state},
        )
    if _expired(run):
        run.patch_state = "expired"
        db.commit()
        raise CopStudioError(
            "PATCH_EXPIRED",
            "This proposal is too old to decide safely. Run the refinement again.",
            status_code=409,
        )
    before = db.scalar(select(Draft).where(Draft.project_id == run.project_id))
    artifact_before = dict(before.artifact_json) if before is not None else None

    run.patch_state = "rejected"
    db.commit()

    # The state change is the only intended effect. Asserting it here rather than
    # trusting it is what makes "rejecting changes nothing" a checked claim.
    if before is not None and artifact_before is not None:
        db.refresh(before)
        assert before.artifact_json == artifact_before, "reject must not modify the draft"

    return PatchResult(
        state="rejected",
        message="Proposal discarded. Your draft and published versions are unchanged.",
    )
