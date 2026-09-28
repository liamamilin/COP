"""Draft API.

Endpoints per the API contract (`10-api-contracts.md` §5):

- `POST   /projects/{project_id}/drafts/from-run/{run_id}`  candidate → draft
- `POST   /projects/{project_id}/drafts/from-version/{version_id}`
- `GET    /projects/{project_id}/draft`
- `PATCH  /drafts/{draft_id}/metadata`
- `PATCH  /drafts/{draft_id}/{entity_type}/{entity_id}`
- `POST   /drafts/{draft_id}/publish`
- `DELETE /drafts/{draft_id}`

Published versions are read-only. There is no PATCH or DELETE for a
`COPVersion` anywhere in this router, and adding one would break the immutability
guarantee in spec 16 §4. The version read endpoints live in `projects.py`.
"""

import uuid
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import CopStudioError, NotFoundError
from app.db.models import COPVersion, Draft, GenerationRun, Project
from app.db.session import get_db
from app.domain.drafting import (
    apply_entity_edit,
    apply_metadata_edit,
    next_version_number,
    resolve_entity_type,
    summarize,
)
from app.domain.validation import validate_artifact
from app.harness.steps.h120_validate import resolve_schema_path

router = APIRouter(tags=["drafts"])
DbSession = Annotated[Session, Depends(get_db)]

# Runs whose candidate may be turned into a draft. `failed` and `cancelled` are
# excluded: their candidate is absent or knowingly incomplete, and the user was
# already told nothing publishable came out of them.
DRAFTABLE_RUN_STATUSES = frozenset({"completed", "needs_attention"})


class DraftSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    base_version_id: uuid.UUID | None
    source_run_id: uuid.UUID | None
    updated_at: datetime
    title: str
    counts: dict[str, int]


class DraftDetail(DraftSummary):
    artifact: dict[str, Any]


class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    version_number: int
    parent_version_id: uuid.UUID | None
    run_id: uuid.UUID | None
    change_summary: str
    created_by: str
    created_at: datetime


class PublishRequest(BaseModel):
    change_summary: str = Field(default="", max_length=1000)


def require_project(db: Session, project_id: uuid.UUID) -> Project:
    """Shared with the rest of the API so 404 bodies stay identical."""
    project = db.get(Project, project_id)
    if project is None or project.status == "deleted":
        raise NotFoundError("Project not found", code="PROJECT_NOT_FOUND")
    return project


def _require_draft(db: Session, draft_id: uuid.UUID) -> Draft:
    draft = db.get(Draft, draft_id)
    if draft is None:
        raise NotFoundError("Draft not found", code="DRAFT_NOT_FOUND")
    return draft


def _draft_out(draft: Draft) -> DraftSummary:
    return DraftSummary(
        id=draft.id,
        project_id=draft.project_id,
        base_version_id=draft.base_version_id,
        source_run_id=draft.source_run_id,
        updated_at=draft.updated_at,
        **summarize(draft.artifact_json),
    )


def _draft_detail(draft: Draft) -> DraftDetail:
    return DraftDetail(**_draft_out(draft).model_dump(), artifact=draft.artifact_json)


def get_active_draft(db: Session, project_id: uuid.UUID) -> Draft | None:
    return db.scalar(select(Draft).where(Draft.project_id == project_id))


def _ensure_no_active_draft(db: Session, project_id: uuid.UUID) -> None:
    """Reject a second draft rather than silently discarding the first.

    A project may have at most one active draft (spec 16 §4). Overwriting it
    would discard edits the user has not published yet, so the existing draft has
    to be published or thrown away first.
    """
    existing = get_active_draft(db, project_id)
    if existing is not None:
        raise CopStudioError(
            "DRAFT_ALREADY_EXISTS",
            "This project already has an active draft. Publish or discard it before "
            "creating another one.",
            status_code=409,
            details={"draft_id": str(existing.id)},
        )


@router.post(
    "/projects/{project_id}/drafts/from-run/{run_id}",
    response_model=DraftDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_draft_from_run(
    project_id: uuid.UUID, run_id: uuid.UUID, db: DbSession
) -> DraftDetail:
    """Turn a finished run's candidate into the project's active draft.

    The run's `base_version_id` carries forward, so a regeneration started from
    v2 publishes as a child of v2 rather than of whatever is newest later.
    """
    require_project(db, project_id)
    run = db.get(GenerationRun, run_id)
    if run is None or run.project_id != project_id:
        raise NotFoundError("Generation run not found in this project", code="RUN_NOT_FOUND")
    if run.status not in DRAFTABLE_RUN_STATUSES:
        raise CopStudioError(
            "CANDIDATE_NOT_AVAILABLE",
            f"A run with status '{run.status}' has no candidate to draft from. Only a "
            "completed run produces a draftable artifact.",
            status_code=409,
            details={"run_status": run.status},
        )
    if not run.candidate_artifact_json:
        raise CopStudioError(
            "CANDIDATE_NOT_READY",
            "This run has not produced a candidate artifact yet",
            status_code=409,
        )
    _ensure_no_active_draft(db, project_id)

    draft = Draft(
        project_id=project_id,
        base_version_id=run.base_version_id,
        source_run_id=run.id,
        artifact_json=run.candidate_artifact_json,
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return _draft_detail(draft)


@router.post(
    "/projects/{project_id}/drafts/from-version/{version_id}",
    response_model=DraftDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_draft_from_version(
    project_id: uuid.UUID, version_id: uuid.UUID, db: DbSession
) -> DraftDetail:
    """Fork a published version into a new editable draft.

    The version itself is untouched; this is how a user revises something already
    live without mutating history.
    """
    require_project(db, project_id)
    version = db.get(COPVersion, version_id)
    if version is None or version.project_id != project_id:
        raise NotFoundError("Version not found in this project", code="VERSION_NOT_FOUND")
    _ensure_no_active_draft(db, project_id)

    draft = Draft(
        project_id=project_id,
        base_version_id=version.id,
        source_run_id=version.run_id,
        artifact_json=version.artifact_json,
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return _draft_detail(draft)


@router.get("/projects/{project_id}/draft", response_model=DraftDetail)
def read_active_draft(project_id: uuid.UUID, db: DbSession) -> DraftDetail:
    require_project(db, project_id)
    draft = get_active_draft(db, project_id)
    if draft is None:
        raise NotFoundError("This project has no active draft", code="DRAFT_NOT_FOUND")
    return _draft_detail(draft)


@router.patch("/drafts/{draft_id}/metadata", response_model=DraftSummary)
def patch_draft_metadata(
    draft_id: uuid.UUID, body: dict[str, Any], db: DbSession
) -> DraftSummary:
    draft = _require_draft(db, draft_id)
    draft.artifact_json = apply_metadata_edit(
        draft.artifact_json, body, schema_path=resolve_schema_path()
    )
    db.commit()
    db.refresh(draft)
    return _draft_out(draft)


@router.patch("/drafts/{draft_id}/{entity_type}/{entity_id}", response_model=DraftSummary)
def patch_draft_entity(
    draft_id: uuid.UUID, entity_type: str, entity_id: str, body: dict[str, Any], db: DbSession
) -> DraftSummary:
    """Edit one entity's text fields in the active draft.

    The path segment is plural (`/processes`) per spec 24 §4, mapped here to the
    singular domain type `process` = `MainProcess`. Reference fields are not
    editable; see `drafting.py`.
    """
    draft = _require_draft(db, draft_id)
    draft.artifact_json = apply_entity_edit(
        draft.artifact_json,
        resolve_entity_type(entity_type) or entity_type,
        entity_id,
        body,
        schema_path=resolve_schema_path(),
    )
    db.commit()
    db.refresh(draft)
    return _draft_out(draft)


@router.post("/drafts/{draft_id}/publish", response_model=VersionOut)
def publish_draft(draft_id: uuid.UUID, body: PublishRequest, db: DbSession) -> VersionOut:
    """Freeze the draft as a new immutable version.

    The next version number is read inside the transaction and the unique
    `(project_id, version_number)` constraint backs it up, so two concurrent
    publishes cannot both claim the same slot.
    """
    draft = _require_draft(db, draft_id)
    project = require_project(db, draft.project_id)

    # Re-validate at publish time. Writes validate too, but publishing is the
    # moment the artifact becomes permanent history, so it gets its own check
    # rather than trusting that no write path was missed.
    try:
        artifact = validate_artifact(draft.artifact_json, resolve_schema_path())
    except Exception as exc:  # noqa: BLE001 - jsonschema and pydantic raise different types
        raise CopStudioError(
            "DRAFT_INVALID",
            f"This draft cannot be published because it is invalid: {exc}",
            status_code=422,
            details={"reason": str(exc)},
        ) from exc

    numbers = list(
        db.scalars(
            select(COPVersion.version_number).where(COPVersion.project_id == project.id)
        )
    )
    parent = db.scalar(
        select(COPVersion)
        .where(COPVersion.project_id == project.id)
        .order_by(COPVersion.version_number.desc())
        .limit(1)
    )
    version = COPVersion(
        project_id=project.id,
        version_number=next_version_number(numbers),
        parent_version_id=parent.id if parent is not None else None,
        run_id=draft.source_run_id,
        artifact_json=artifact.model_dump(mode="json"),
        change_summary=body.change_summary.strip() or "Manual draft published",
        created_by="user",
    )
    db.add(version)
    # The draft is now a version. Leaving it in place would leave the project
    # with an active draft that silently shadows the version just published.
    db.delete(draft)
    db.commit()
    db.refresh(version)
    return VersionOut.model_validate(version)


@router.delete("/drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
def discard_draft(draft_id: uuid.UUID, db: DbSession) -> None:
    """Throw the draft away. Published versions are unaffected."""
    draft = _require_draft(db, draft_id)
    db.delete(draft)
    db.commit()
