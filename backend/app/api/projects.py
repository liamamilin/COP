import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.db.models import COPVersion, Project
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
    preferred_language: str = Field(default="auto", max_length=32)


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


def _project_query() -> Select[tuple[Project, int | None]]:
    return (
        select(Project, func.max(COPVersion.version_number))
        .outerjoin(COPVersion, COPVersion.project_id == Project.id)
        .where(Project.status != "deleted")
        .group_by(Project.id)
        .order_by(Project.updated_at.desc())
    )


def _version_detail(version: COPVersion) -> VersionDetail:
    summary = VersionSummary.model_validate(version)
    return VersionDetail(**summary.model_dump(), artifact=version.artifact_json)


@router.get("/projects", response_model=list[ProjectSummary])
def list_projects(db: DbSession, include_archived: bool = False) -> list[ProjectSummary]:
    query = _project_query()
    if not include_archived:
        query = query.where(Project.status == "active")
    return [
        ProjectSummary.model_validate(project).model_copy(update={"latest_version": version})
        for project, version in db.execute(query).all()
    ]


@router.post("/projects", response_model=ProjectSummary, status_code=status.HTTP_201_CREATED)
def create_project(body: ProjectCreate, db: DbSession) -> ProjectSummary:
    project = Project(**body.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectSummary.model_validate(project)


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
def duplicate_project(project_id: uuid.UUID, db: DbSession) -> ProjectSummary:
    source = db.get(Project, project_id)
    if source is None or source.status == "deleted":
        raise HTTPException(status_code=404, detail="Project not found")
    duplicate = Project(
        title=f"{source.title} copy",
        description=source.description,
        domain=source.domain,
        scope=source.scope,
        preferred_language=source.preferred_language,
    )
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    return ProjectSummary.model_validate(duplicate)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: uuid.UUID, db: DbSession) -> None:
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
    return _version_detail(version)


@router.get("/versions/{version_id}", response_model=VersionDetail)
def get_version(version_id: uuid.UUID, db: DbSession) -> VersionDetail:
    version = db.get(COPVersion, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Version not found")
    return _version_detail(version)
