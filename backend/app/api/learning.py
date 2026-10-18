"""Learning progress API.

Endpoints per `10-api-contracts.md` §7:

- `GET /projects/{project_id}/learning-progress?version_id=...`
- `PUT /projects/{project_id}/learning-progress`

Six rules, each from `16-state-machines.md` §6, the M7 acceptance criteria, or
R5:

- Progress belongs to a **version**, never to a project.
- A Stage may go `completed -> in_progress`, because revisiting is legitimate.
- **Goal completion is derived, never stored.** Storing it would need
  invalidating every time a Stage is revisited, and it would eventually disagree
  with the rows it came from.
- **Shared Foundation progress is keyed per Stage, not per Goal.** Every Main
  Process starts at the same Foundation Stages; storing those N times would make
  "have I learned this?" depend on which Goal you happened to be looking at.
- **A Practice is not complete until its minimal checkpoint is answered.** A
  checkbox that clears without an answer records nothing.
- **Foundation Stages count toward every Goal that depends on them**, because
  the alternative is a Goal showing complete while the setup it depends on is
  still open.
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
ActivityKind = Literal["stage", "foundation", "practice", "checkpoint"]

#: `not_started` is the absence of a row, so a reset writes nothing.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    None: {"not_started", "in_progress", "completed"},
    "not_started": {"not_started", "in_progress", "completed"},
    "in_progress": {"in_progress", "completed"},
    "completed": {"completed", "in_progress"},
}


class ProgressUpdate(BaseModel):
    version_id: uuid.UUID
    #: Which activity this row describes. `stage` for a Main Process Stage,
    #: `foundation` for a Shared Foundation Stage, `practice` for a Practice,
    #: `checkpoint` for one checkpoint answer.
    kind: ActivityKind = "stage"
    #: Empty only for `kind="foundation"`, where the row belongs to no Goal. The
    #: Pydantic constraint is `min_length=0` here rather than `1` because the
    #: empty value is load-bearing: a Foundation row must not carry a Goal, or
    #: the shared setup would be recorded once per Goal that starts at it.
    goal_id: str = Field(default="", max_length=180)
    stage_id: str | None = Field(default=None, max_length=180)
    status: StageStatus = "in_progress"
    notes: str | None = Field(default=None, max_length=4000)


class StageProgress(BaseModel):
    stage_id: str
    status: StageStatus
    notes: str | None = None
    updated_at: Any = None


class FoundationStageProgress(BaseModel):
    stage_id: str
    status: StageStatus
    updated_at: Any = None


class CheckpointProgress(BaseModel):
    """One question's answer.

    Answered rather than merely ticked: a checkpoint exists so completion means
    something, and a checkbox that clears without an answer is indistinguishable
    from one that was never read.
    """

    question: str
    answer: str | None = None
    updated_at: Any = None


class PracticeProgress(BaseModel):
    practice_id: str
    title: str
    status: StageStatus
    checkpoints: list[CheckpointProgress] = []
    updated_at: Any = None


class GoalProgress(BaseModel):
    goal_id: str
    title: str
    completed: bool
    total_stages: int
    completed_stages: int
    #: Why the Goal is not complete, when it is not. A Goal showing an empty
    #: progress bar with no reason is the same as a broken progress bar.
    blocked_by: list[str] = []
    stages: list[StageProgress]
    practice: PracticeProgress | None = None


class ProgressOut(BaseModel):
    project_id: uuid.UUID
    version_id: uuid.UUID
    version_number: int
    goals: list[GoalProgress]
    foundations: list[FoundationStageProgress]
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


def _required_foundation_ids(artifact: dict[str, Any]) -> set[str]:
    """Foundation Stages this artifact declares, deduplicated.

    Read from `shared_foundations` rather than inferred from the Main Processes'
    `start` refs, because the foundation is the thing that exists once and is
    shared; inferring it per process would create several copies of one Stage.
    """
    found: set[str] = set()
    for foundation in artifact.get("shared_foundations") or []:
        for stage_id in foundation.get("stage_refs") or []:
            found.add(str(stage_id))
    return found


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
    by_stage = {row.stage_id: row for row in rows if row.stage_id and row.kind == "stage"}
    by_foundation = {row.stage_id: row for row in rows if row.stage_id and row.kind == "foundation"}
    practices = {row.goal_id: row for row in rows if row.kind == "practice"}
    checkpoints = [row for row in rows if row.kind == "checkpoint"]

    artifact = version.artifact_json
    required_foundations = _required_foundation_ids(artifact)

    foundations = [
        FoundationStageProgress(
            stage_id=stage_id,
            status=(by_foundation[stage_id].status if stage_id in by_foundation else "not_started"),
            updated_at=by_foundation[stage_id].updated_at if stage_id in by_foundation else None,
        )
        for stage_id in sorted(required_foundations)
    ]
    foundations_done = sum(1 for item in foundations if item.status == "completed")

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

        practice_entity = next(
            (
                item
                for item in artifact.get("practices") or []
                if str(item.get("goal_ref")) == goal_id
            ),
            None,
        )
        practice_progress = _practice_progress(practice_entity, practices.get(goal_id), checkpoints)

        # Derived, in the order a learner would meet the blockers.
        blocked_by: list[str] = []
        if foundations_done < len(foundations):
            blocked_by.append(
                f"Shared Foundation: {foundations_done} of {len(foundations)} stages complete"
            )
        if done < len(stages):
            blocked_by.append(f"Stages: {done} of {len(stages)} complete")
        if practice_entity is not None:
            if practice_progress is None or practice_progress.status == "not_started":
                blocked_by.append("Minimal Practice not started")
            elif practice_progress.status != "completed":
                unanswered = [
                    item
                    for item in practice_progress.checkpoints
                    if not (item.answer or "").strip()
                ]
                blocked_by.append(
                    "Minimal Practice: "
                    + (
                        f"{len(unanswered)} checkpoint question(s) unanswered"
                        if unanswered
                        else "practice not marked complete"
                    )
                )

        goals.append(
            GoalProgress(
                goal_id=goal_id,
                title=str(goal.get("title") or goal_id),
                # A Goal with no Stages of its own is complete when its Foundation
                # and Practice are; otherwise it could never be.
                completed=not blocked_by,
                total_stages=len(stages),
                completed_stages=done,
                blocked_by=blocked_by,
                stages=stages,
                practice=practice_progress,
            )
        )

    return ProgressOut(
        project_id=project_id,
        version_id=version.id,
        version_number=version.version_number,
        goals=goals,
        foundations=foundations,
        completed_goals=sum(1 for goal in goals if goal.completed),
        total_goals=len(goals),
    )


def _practice_progress(
    practice: dict[str, Any] | None,
    row: LearningProgress | None,
    checkpoints: list[LearningProgress],
) -> PracticeProgress | None:
    """Practice status, with each checkpoint's answer attached.

    A checkpoint is keyed by the question text stored in `notes`, which is why a
    checkpoint row's `notes` is the answer and its identity comes from
    `stage_id`, which holds the question. Storing the question as the key means a
    reworded question produces a new row rather than silently overwriting the
    learner's answer to the old one.
    """
    if practice is None:
        return None
    questions = [str(item) for item in practice.get("checkpoint_questions") or []]
    answers = {row.stage_id: row for row in checkpoints if row.stage_id}
    answered = [answers[question] for question in questions if question in answers]

    # Derived, not just read off the practice row. A learner who answers a
    # question has demonstrably started, and if the derived status stayed
    # `not_started` until they ticked the box, the app would tell someone working
    # through the exercise that they had not begun.
    if row is not None:
        status = row.status
    elif answered:
        status = "in_progress"
    else:
        status = "not_started"

    return PracticeProgress(
        practice_id=str(practice.get("id", "")),
        title=str(practice.get("title", "")),
        status=status,
        updated_at=max(
            (item.updated_at for item in [row, *answered] if item is not None and item.updated_at),
            default=None,
        ),
        checkpoints=[
            CheckpointProgress(
                question=question,
                answer=(answers[question].notes if question in answers else None),
                updated_at=(answers[question].updated_at if question in answers else None),
            )
            for question in questions
        ],
    )


@router.put("/projects/{project_id}/learning-progress")
def put_learning_progress(
    project_id: uuid.UUID, body: ProgressUpdate, db: DbSession
) -> dict[str, Any]:
    """Record progress for one Stage, Practice, or checkpoint answer."""
    _require_project(db, project_id)
    version = _require_version(db, project_id, body.version_id)
    artifact = version.artifact_json
    goal_ids = {str(item.get("id")) for item in artifact.get("goals") or []}
    required_foundations = _required_foundation_ids(artifact)

    if body.kind == "stage" and not body.goal_id:
        raise CopStudioError(
            "GOAL_REQUIRED",
            "A Main Process Stage belongs to a Goal. Send the Goal it is on.",
            status_code=422,
        )
    if body.kind in {"stage", "practice"} and body.goal_id not in goal_ids:
        raise CopStudioError(
            "GOAL_NOT_IN_VERSION",
            f"Goal '{body.goal_id}' is not part of version {version.version_number}.",
            status_code=422,
        )
    if body.kind == "practice":
        practice = _practice_for_goal(artifact, body.goal_id)
        if not practice:
            raise CopStudioError(
                "NO_PRACTICE_FOR_GOAL",
                f"Goal '{body.goal_id}' has no Minimal Practice to record progress for.",
                status_code=422,
            )
        if body.stage_id:
            # A practice row is keyed by Goal, so a stray stage_id would create a
            # second row for the same Practice and the reads would disagree about
            # which one is real.
            raise CopStudioError(
                "PRACTICE_TAKES_NO_STAGE",
                "A Minimal Practice belongs to a Goal, not a Stage. Send an empty stage_id.",
                status_code=422,
            )

    if body.kind in {"stage", "foundation"}:
        _validate_stage(db, artifact, body, goal_ids, required_foundations)
    if body.kind == "checkpoint":
        _validate_checkpoint(artifact, body, goal_ids)

    existing = db.scalar(
        select(LearningProgress).where(
            LearningProgress.project_id == project_id,
            LearningProgress.version_id == version.id,
            LearningProgress.kind == body.kind,
            func.coalesce(LearningProgress.goal_id, "") == (body.goal_id or ""),
            func.coalesce(LearningProgress.stage_id, "") == (body.stage_id or ""),
        )
    )
    current = existing.status if existing is not None else None
    if body.status not in ALLOWED_TRANSITIONS.get(current, set()):
        raise CopStudioError(
            "INVALID_PROGRESS_TRANSITION",
            f"A {body.kind} cannot move from '{current or 'not_started'}' to '{body.status}'.",
            status_code=409,
            details={"from": current or "not_started", "to": body.status},
        )

    # Upsert rather than select-then-write: two devices marking the same activity
    # done at once would otherwise create two rows. The conflict target is the
    # expression index, not a named constraint -- Postgres's
    # `ON CONFLICT ON CONSTRAINT` only accepts real constraints, and a unique
    # index built on an expression is not one.
    statement = insert(LearningProgress).values(
        id=existing.id if existing is not None else uuid.uuid4(),
        project_id=project_id,
        version_id=version.id,
        kind=body.kind,
        goal_id=body.goal_id,
        stage_id=body.stage_id,
        status=body.status,
        notes=body.notes,
    )
    statement = statement.on_conflict_do_update(
        index_elements=[
            LearningProgress.version_id,
            LearningProgress.kind,
            func.coalesce(LearningProgress.goal_id, ""),
            func.coalesce(LearningProgress.stage_id, ""),
        ],
        set_={"status": body.status, "notes": body.notes},
    )
    db.execute(statement)
    db.commit()
    return {
        "status": body.status,
        "kind": body.kind,
        "version_id": str(version.id),
        "goal_id": body.goal_id,
        "stage_id": body.stage_id,
    }


def _practice_for_goal(artifact: dict[str, Any], goal_id: str) -> dict[str, Any] | None:
    return next(
        (item for item in artifact.get("practices") or [] if str(item.get("goal_ref")) == goal_id),
        None,
    )


def _validate_stage(
    db: Session,
    artifact: dict[str, Any],
    body: ProgressUpdate,
    goal_ids: set[str],
    required_foundations: set[str],
) -> None:
    """A Stage row must name a Stage that exists, in the right place.

    A Foundation Stage belongs to no Goal, so `goal_id` is accepted as the empty
    string for it. Writing a Foundation row under a Goal would be the M7 bug all
    over again: the same Stage recorded once per Goal that starts at it.
    """
    if body.stage_id is None:
        raise CopStudioError(
            "STAGE_ID_REQUIRED",
            f"A {body.kind} progress row needs the Stage it refers to.",
            status_code=422,
        )
    known_stage_ids = {str(item.get("id")) for item in artifact.get("stages") or []}
    if body.stage_id not in known_stage_ids:
        raise CopStudioError(
            "STAGE_NOT_IN_VERSION",
            f"Stage '{body.stage_id}' is not part of version {body.version_id}.",
            status_code=422,
        )
    if body.kind == "foundation":
        if body.stage_id not in required_foundations:
            raise CopStudioError(
                "STAGE_NOT_FOUNDATION",
                f"Stage '{body.stage_id}' is not a Shared Foundation Stage.",
                status_code=422,
            )
        if body.goal_id:
            raise CopStudioError(
                "FOUNDATION_NEEDS_NO_GOAL",
                "A Shared Foundation Stage belongs to no Goal. Send an empty goal_id.",
                status_code=422,
            )
        return
    if body.stage_id not in _stages_for_goal(artifact, body.goal_id):
        raise CopStudioError(
            "STAGE_NOT_IN_GOAL",
            f"Stage '{body.stage_id}' does not belong to this Goal's Main Process.",
            status_code=422,
            details={"expected_stages": _stages_for_goal(artifact, body.goal_id)},
        )


def _validate_checkpoint(
    artifact: dict[str, Any], body: ProgressUpdate, goal_ids: set[str]
) -> None:
    """A checkpoint answer must quote a question the Practice actually asks.

    Otherwise the row is an answer to a question nobody posed, and the Practice
    would look answered.
    """
    if body.goal_id not in goal_ids:
        raise CopStudioError(
            "GOAL_NOT_IN_VERSION",
            f"Goal '{body.goal_id}' is not part of version {body.version_id}.",
            status_code=422,
        )
    practice = _practice_for_goal(artifact, body.goal_id)
    questions = [str(item) for item in (practice or {}).get("checkpoint_questions") or []]
    if body.stage_id not in questions:
        raise CopStudioError(
            "CHECKPOINT_NOT_IN_PRACTICE",
            "That question is not one this Goal's Minimal Practice asks.",
            status_code=422,
            details={"questions": questions},
        )
    if not (body.notes or "").strip():
        # An empty answer is a cleared answer, which the UI sends as a delete.
        # Refusing here would make it impossible to un-answer a question.
        raise CopStudioError(
            "CHECKPOINT_ANSWER_REQUIRED",
            "A checkpoint answer cannot be empty. Clear the question instead.",
            status_code=422,
        )
