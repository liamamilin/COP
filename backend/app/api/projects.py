import copy
import uuid
from datetime import datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.api.settings import deep_merge
from app.db.models import COPVersion, Project, ProjectSettings, Source, SourceDocument
from app.db.session import get_db

router = APIRouter(tags=["projects"])
DbSession = Annotated[Session, Depends(get_db)]


class ProjectSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    domain: str
    scope: str
    preferred_language: str
    status: str
    created_at: datetime
    updated_at: datetime
    latest_version: int | None = None


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    domain: str = Field(min_length=1, max_length=240)
    scope: str = ""
    description: str = ""
    # Validated against the same set the Harness and Settings use. A language the
    # rest of the system has never heard of would be accepted here and then
    # ignored downstream, which is the failure this whole batch is about.
    # Validated against the same set the Harness and Settings use. A language the
    # rest of the system has never heard of would be accepted here and then
    # ignored downstream, which is the failure this whole batch is about.
    preferred_language: str = Field(
        default="auto", max_length=32, pattern=r"^(auto|en|zh-CN|ja|ko|fr|de|es|pt|ru|it)$"
    )
    # Accepted at creation so the first run already matches the form the user
    # filled in. It used to be dropped here and offered only in the app-wide
    # Settings, which meant a per-project choice silently did nothing.
    learner_level: Literal["new", "some_experience", "advanced"] = "new"
    # Accepted at creation so the first run already matches the form the user
    # filled in. It used to be dropped here and offered only in the app-wide
    # Settings, which meant a per-project choice silently did nothing.
    learner_level: Literal["new", "some_experience", "advanced"] = "new"


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    domain: str | None = Field(default=None, min_length=1, max_length=240)
    scope: str | None = None
    description: str | None = None
    preferred_language: str | None = Field(default=None, max_length=32)
    status: str | None = Field(default=None, pattern="^(active|archived)$")


class VersionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    version_number: int
    # Null for the first published version; set on every later one, which is what
    # makes v2 record that it descends from v1.
    parent_version_id: uuid.UUID | None
    run_id: uuid.UUID | None
    change_summary: str
    created_by: str
    created_at: datetime


class VersionDetail(VersionSummary):
    artifact: dict
    # `evidence_ref.source_id` -> the project Source it resolves to. Only the
    # refs that actually resolve appear, so a missing key *is* the signal that a
    # citation is unopenable.
    evidence_sources: dict[str, dict[str, Any]] = {}


def _project_query() -> Select[tuple[Project, int | None]]:
    return (
        select(Project, func.max(COPVersion.version_number))
        .outerjoin(COPVersion, COPVersion.project_id == Project.id)
        .where(Project.status != "deleted")
        .group_by(Project.id)
        .order_by(Project.updated_at.desc())
    )


def _version_detail(version: COPVersion, db: Session) -> VersionDetail:
    """The version, its artifact, and an evidence resolution for that artifact.

    The evidence map is resolved here rather than left to the browser, because
    "can the user open this citation" is a question about the project's sources,
    which only the backend knows. The client receives a plain `source_id ->
    source` map and does no lookups of its own.
    """
    from app.api.drafts import evidence_refs
    from app.jobs.runner import project_source_ids

    summary = VersionSummary.model_validate(version)
    wanted = {item["source_id"] for item in evidence_refs(version.artifact_json or {})}
    known = project_source_ids(db, version.project_id)

    resolved: dict[str, dict[str, Any]] = {}
    if wanted:
        rows = db.scalars(select(Source).where(Source.project_id == version.project_id))
        for source in rows:
            sid = str(source.id)
            research_id = str((source.metadata_json or {}).get("research_source_id") or "")
            for candidate in (sid, research_id) if research_id else (sid,):
                if candidate in wanted and candidate in known:
                    resolved[candidate] = {
                        "id": sid,
                        "title": source.title,
                        "type": source.type,
                        "uri": source.original_uri,
                        "status": source.status,
                    }
    return VersionDetail(
        **summary.model_dump(),
        artifact=version.artifact_json,
        evidence_sources=resolved,
    )


@router.get("/projects", response_model=list[ProjectSummary])
def list_projects(
    db: DbSession, include_archived: bool = False, status: str | None = None
) -> list[ProjectSummary]:
    """List projects.

    `status` filters exactly, so the archived view can ask for `archived`
    without also receiving the active ones. `include_archived` stays for
    compatibility and means "both".

    Archived projects are hidden by default rather than deleted: spec `18`
    requires both "archive/delete project" and "project list survives restart",
    and a user who cannot find a project they archived has lost it in practice.
    """
    query = _project_query()
    if status:
        query = query.where(Project.status == status)
    elif not include_archived:
        query = query.where(Project.status == "active")
    return [
        ProjectSummary.model_validate(project).model_copy(update={"latest_version": version})
        for project, version in db.execute(query).all()
    ]


@router.post("/projects", response_model=ProjectSummary, status_code=status.HTTP_201_CREATED)
def create_project(body: ProjectCreate, db: DbSession) -> ProjectSummary:
    # `learner_level` is not a Project column: it is a generation setting, and it
    # belongs to the same hierarchy as every other one. Writing it into
    # project_settings here is what makes "new project, pick advanced" mean
    # something on the first run.
    fields = body.model_dump()
    learner_level = fields.pop("learner_level")
    project = Project(**fields)
    db.add(project)
    db.flush()
    _merge_project_generation(
        db,
        project.id,
        {"language": body.preferred_language, "learner_level": learner_level},
    )
    db.commit()
    db.refresh(project)
    return ProjectSummary.model_validate(project)


def _merge_project_generation(
    db: Session, project_id: uuid.UUID, generation: dict[str, Any]
) -> None:
    """Write project-level generation settings, preserving anything already set.

    `deep_merge` rather than an overwrite: creating a project should not be able
    to silently reset a generation override a user set moments earlier.
    """
    record = db.get(ProjectSettings, project_id)
    if record is None:
        db.add(ProjectSettings(project_id=project_id, settings_json={"generation": generation}))
        return
    record.settings_json = deep_merge(record.settings_json, {"generation": generation})


@router.get("/projects/{project_id}", response_model=ProjectSummary)
def get_project(project_id: uuid.UUID, db: DbSession) -> ProjectSummary:
    row = db.execute(_project_query().where(Project.id == project_id)).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    project, version = row
    return ProjectSummary.model_validate(project).model_copy(update={"latest_version": version})


@router.patch("/projects/{project_id}", response_model=ProjectSummary)
def update_project(project_id: uuid.UUID, body: ProjectUpdate, db: DbSession) -> ProjectSummary:
    project = db.get(Project, project_id)
    if project is None or project.status == "deleted":
        raise HTTPException(status_code=404, detail="Project not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    latest_version = db.scalar(
        select(func.max(COPVersion.version_number)).where(COPVersion.project_id == project.id)
    )
    return ProjectSummary.model_validate(project).model_copy(
        update={"latest_version": latest_version}
    )


@router.post("/projects/{project_id}/duplicate", response_model=ProjectSummary)
def duplicate_project(
    project_id: uuid.UUID, db: DbSession, with_sources: bool = True
) -> ProjectSummary:
    """Create an independent copy of a project.

    The copy shares no rows with the original: its own sources, its own
    versions, its own learning progress. A duplicate that shared them would be a
    second name for one project, and deleting either would take the other with
    it.

    Sources and the latest published version are copied because a duplicate with
    nothing in it is not something anyone can use. The version is copied rather
    than re-generated: re-running the Harness would produce a different COP, and
    the point of a duplicate is to try a revision from a known starting point.
    """
    source = db.get(Project, project_id)
    if source is None or source.status == "deleted":
        raise HTTPException(status_code=404, detail="Project not found")

    duplicate = Project(
        title=f"{source.title} (copy)",
        description=source.description,
        domain=source.domain,
        scope=source.scope,
        preferred_language=source.preferred_language,
    )
    db.add(duplicate)
    db.flush()

    # Generation settings travel with the project, otherwise a duplicate silently
    # regenerates in a different language or depth than the original.
    source_settings = db.get(ProjectSettings, project_id)
    if source_settings is not None and source_settings.settings_json:
        db.add(
            ProjectSettings(
                project_id=duplicate.id,
                settings_json=copy.deepcopy(source_settings.settings_json),
            )
        )

    if with_sources:
        _copy_sources(db, project_id, duplicate.id)
        _copy_latest_version(db, project_id, duplicate.id)

    db.commit()
    db.refresh(duplicate)
    row = db.execute(_project_query().where(Project.id == duplicate.id)).one_or_none()
    latest = row[1] if row else None
    return ProjectSummary.model_validate(duplicate).model_copy(update={"latest_version": latest})


def _copy_sources(db: Session, from_project: uuid.UUID, to_project: uuid.UUID) -> None:
    """Copy Source rows and their extracted text.

    The blob path is not reused: two Sources pointing at one file on disk would
    mean deleting one could take the other's text with it. The extracted text is
    in `source_documents`, so a copy is a row copy rather than a file operation.
    """
    rows = db.execute(
        select(Source, SourceDocument)
        .outerjoin(SourceDocument, SourceDocument.source_id == Source.id)
        .where(Source.project_id == from_project)
    ).all()
    for source, document in rows:
        clone = Source(
            project_id=to_project,
            type=source.type,
            title=source.title,
            original_uri=source.original_uri,
            status=source.status,
            metadata_json=copy.deepcopy(source.metadata_json or {}),
        )
        db.add(clone)
        db.flush()
        if document is not None:
            db.add(
                SourceDocument(
                    source_id=clone.id,
                    text=document.text,
                    text_path=None,
                    content_hash=document.content_hash,
                    char_count=document.char_count,
                    metadata_json=copy.deepcopy(document.metadata_json or {}),
                )
            )


def _copy_latest_version(db: Session, from_project: uuid.UUID, to_project: uuid.UUID) -> None:
    latest = db.scalar(
        select(COPVersion)
        .where(COPVersion.project_id == from_project)
        .order_by(COPVersion.version_number.desc())
        .limit(1)
    )
    if latest is None:
        return
    db.add(
        COPVersion(
            project_id=to_project,
            # Always v1 in the copy. Keeping the original's number would imply a
            # history the copy does not have.
            version_number=1,
            parent_version_id=None,
            run_id=None,
            artifact_json=copy.deepcopy(latest.artifact_json),
            change_summary=f"Copied from {from_project}",
            created_by="user",
        )
    )


@router.post("/projects/{project_id}/restore", response_model=ProjectSummary)
def restore_project(project_id: uuid.UUID, db: DbSession) -> ProjectSummary:
    """Bring an archived project back.

    Only the status changes. Sources, versions, and learning progress are all
    still there, which is the entire reason Archive exists and Delete does not.
    """
    project = db.get(Project, project_id)
    if project is None or project.status == "deleted":
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status == "active":
        return ProjectSummary.model_validate(project)
    project.status = "active"
    db.commit()
    db.refresh(project)
    row = db.execute(_project_query().where(Project.id == project_id)).one_or_none()
    latest = row[1] if row else None
    return ProjectSummary.model_validate(project).model_copy(update={"latest_version": latest})


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: uuid.UUID, db: DbSession) -> None:
    """Soft-delete a project.

    A status change, not a row removal. The distinction matters to the user: the
    API reports 204 and the project leaves the active list, but nothing is
    destroyed, and the published versions remain readable. The UI says so before
    asking, because "delete" is the word that makes people hesitate.
    """
    project = db.get(Project, project_id)
    if project is None or project.status == "deleted":
        raise HTTPException(status_code=404, detail="Project not found")
    project.status = "deleted"
    db.commit()


@router.get("/projects/{project_id}/versions", response_model=list[VersionSummary])
def list_versions(project_id: uuid.UUID, db: DbSession) -> list[COPVersion]:
    return list(
        db.scalars(
            select(COPVersion)
            .where(COPVersion.project_id == project_id)
            .order_by(COPVersion.version_number.desc())
        )
    )


@router.get("/projects/{project_id}/versions/latest", response_model=VersionDetail)
def get_latest_version(project_id: uuid.UUID, db: DbSession) -> VersionDetail:
    version = db.scalar(
        select(COPVersion)
        .where(COPVersion.project_id == project_id)
        .order_by(COPVersion.version_number.desc())
        .limit(1)
    )
    if version is None:
        raise HTTPException(status_code=404, detail="No published COP version")
    return _version_detail(version, db)


@router.get("/versions/{version_id}", response_model=VersionDetail)
def get_version(version_id: uuid.UUID, db: DbSession) -> VersionDetail:
    version = db.get(COPVersion, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Version not found")
    return _version_detail(version, db)
