"""Learning progress API.

Endpoints per `10-api-contracts.md` §7:

- `GET /projects/{project_id}/learning-progress?version_id=...`
- `PUT /projects/{project_id}/learning-progress`

Three rules, from `16-state-machines.md` §6 and the M7 acceptance criteria:

- Progress belongs to a **version**, never to a project. Switching versions
  must show a different, intact history rather than overwrite it.
- A Stage may go `completed -> in_progress`, because revisiting and resetting is
  legitimate. Everything else follows the documented order.
- Goal completion is **derived**, not stored. Storing it would need invalidating
  every time a Stage is revisited, and it would eventually disagree with the
  Stage rows it was derived from.
"""

import uuid
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.errors import CopStudioError, NotFoundError
from app.db.models import COPVersion, LearningProgress, Project
from app.db.session import get_db

router = APIRouter(tags=["learning"])
DbSession = Annotated[Session, Depends(get_db)]

StageStatus = Literal["not_started", "in_progress", "completed"]

# `not_started` is represented by the absence of a row rather than a row saying
# "not started", so a reset does not have to write anything.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    None: {"not_started", "in_progress", "completed"},
    "not_started": {"not_started", "in_progress", "completed"},
    "in_progress": {"in_progress", "completed"},
    "completed": {"completed", "in_progress"},
}


class ProgressUpdate(BaseModel):
    version_id: uuid.UUID
    goal_id: str = Field(min_length=1, max_length=180)
    stage_id: str | None = Field(default=None, max_length=180)
    status: StageStatus = "in_progress"
    notes: str | None = Field(default=None, max_length=4000)


class StageProgress(BaseModel):
    stage_id: str
    status: StageStatus
    notes: str | None = None
    updated_at: Any = None


class GoalProgress(BaseModel):
    goal_id: str
    title: str
    completed: bool
    total_stages: int
    completed_stages: int
    stages: list[StageProgress]


class ProgressOut(BaseModel):
    project_id: uuid.UUID
    version_id: uuid.UUID
    version_number: int
    goals: list[GoalProgress]
    completed_goals: int
    total_goals: int


def _require_project(db: Session, project_id: uuid.UUID) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.status == "deleted":
        raise NotFoundError("Project not found", code="PROJECT_NOT_FOUND")
    return project


def _require_version(db: Session, project_id: uuid.UUID, version_id: uuid.UUID) -> COPVersion:
    version = db.get(COPVersion, version_id)
    if version is None or version.project_id != project_id:
        raise NotFoundError("Version not found in this project", code="VERSION_NOT_FOUND")
    return version


def _stages_for_goal(artifact: dict[str, Any], goal_id: str) -> list[str]:
    """Every Stage the Goal's Main Process runs through, in order."""
    process = next(
        (
            item
            for item in (artifact.get("main_processes") or [])
            if item.get("goal_ref") == goal_id
        ),
        None,
    )
    return [str(item) for item in (process or {}).get("stage_refs") or []]


@router.get("/projects/{project_id}/learning-progress", response_model=ProgressOut)
def get_learning_progress(
    project_id: uuid.UUID,
    db: DbSession,
    version_id: uuid.UUID | None = None,
) -> ProgressOut:
    """Progress for one version of the COP.

    Scoped to a version on purpose. Reading without one defaults to the latest
    version, which is what a user opening Learn Mode wants, but the id is
    explicit in the response so a stale tab cannot write into the wrong history.
    """
    _require_project(db, project_id)
    if version_id is None:
        version = db.scalar(
            select(COPVersion)
            .where(COPVersion.project_id == project_id)
            .order_by(COPVersion.version_number.desc())
            .limit(1)
        )
        if version is None:
            raise NotFoundError("This project has no published COP version", code="NO_VERSION")
    else:
        version = _require_version(db, project_id, version_id)

    rows = list(
        db.scalars(
            select(LearningProgress).where(
                LearningProgress.project_id == project_id,
                LearningProgress.version_id == version.id,
            )
        )
    )
    by_stage = {row.stage_id: row for row in rows if row.stage_id}
    artifact = version.artifact_json

    goals: list[GoalProgress] = []
    for goal in artifact.get("goals") or []:
        goal_id = str(goal.get("id"))
        stage_ids = _stages_for_goal(artifact, goal_id)
        stages: list[StageProgress] = []
        for stage_id in stage_ids:
            row = by_stage.get(stage_id)
            stages.append(
                StageProgress(
                    stage_id=stage_id,
                    status=(row.status if row else "not_started"),
                    notes=row.notes if row else None,
                    updated_at=row.updated_at if row else None,
                )
            )
        done = sum(1 for item in stages if item.status == "completed")
        goals.append(
            GoalProgress(
                goal_id=goal_id,
                title=str(goal.get("title") or goal_id),
                completed=bool(stage_ids) and done == len(stage_ids),
                total_stages=len(stage_ids),
                completed_stages=done,
                stages=stages,
            )
        )

    return ProgressOut(
        project_id=project_id,
        version_id=version.id,
        version_number=version.version_number,
        goals=goals,
        completed_goals=sum(1 for goal in goals if goal.completed),
        total_goals=len(goals),
    )


@router.put("/projects/{project_id}/learning-progress")
def put_learning_progress(
    project_id: uuid.UUID, body: ProgressUpdate, db: DbSession
) -> dict[str, Any]:
    """Record progress for one Stage, or for a Goal as a whole.

    `stage_id` is optional: a Goal-level row records the user's explicit
    completion, which the spec allows when the project permits it.
    """
    _require_project(db, project_id)
    version = _require_version(db, project_id, body.version_id)

    artifact = version.artifact_json
    goal = next(
        (item for item in (artifact.get("goals") or []) if str(item.get("id")) == body.goal_id),
        None,
    )
    if goal is None:
        raise CopStudioError(
            "GOAL_NOT_IN_VERSION",
            f"Goal '{body.goal_id}' is not part of version {version.version_number}.",
            status_code=422,
        )

    if body.stage_id is not None:
        allowed = _stages_for_goal(artifact, body.goal_id)
        if body.stage_id not in allowed:
            raise CopStudioError(
                "STAGE_NOT_IN_GOAL",
                f"Stage '{body.stage_id}' does not belong to this Goal's Main Process.",
                status_code=422,
                details={"expected_stages": allowed},
            )

    existing = db.scalar(
        select(LearningProgress).where(
            LearningProgress.project_id == project_id,
            LearningProgress.version_id == version.id,
            LearningProgress.goal_id == body.goal_id,
            func.coalesce(LearningProgress.stage_id, "") == (body.stage_id or ""),
        )
    )
    current = existing.status if existing is not None else None
    if body.status not in ALLOWED_TRANSITIONS.get(current, set()):
        raise CopStudioError(
            "INVALID_PROGRESS_TRANSITION",
            f"A Stage cannot move from '{current or 'not_started'}' to '{body.status}'.",
            status_code=409,
            details={"from": current or "not_started", "to": body.status},
        )

    # Upsert rather than select-then-write: two devices marking the same Stage
    # done at once would otherwise create two rows. The conflict target is the
    # expression index, not a named constraint -- Postgres's
    # `ON CONFLICT ON CONSTRAINT` only accepts real constraints, and a unique
    # index built on an expression is not one.
    statement = insert(LearningProgress).values(
        id=existing.id if existing is not None else uuid.uuid4(),
        project_id=project_id,
        version_id=version.id,
        goal_id=body.goal_id,
        stage_id=body.stage_id,
        status=body.status,
        notes=body.notes,
    )
    statement = statement.on_conflict_do_update(
        index_elements=[
            LearningProgress.version_id,
            LearningProgress.goal_id,
            func.coalesce(LearningProgress.stage_id, ""),
        ],
        set_={"status": body.status, "notes": body.notes},
    )
    db.execute(statement)
    db.commit()
    return {"status": body.status, "version_id": str(version.id), "stage_id": body.stage_id}
