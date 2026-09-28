import uuid
from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Project, Source, SourceDocument
from app.db.session import get_db
from app.sources.extractors import SourceExtractionError
from app.sources.service import get_blob_store, process_source, safe_upload_name

router = APIRouter(tags=["sources"])
DbSession = Annotated[Session, Depends(get_db)]


class TextSourceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    text: str = Field(min_length=1)
    format: Literal["text", "markdown"] = "text"


class URLSourceCreate(BaseModel):
    url: HttpUrl
    title: str | None = Field(default=None, max_length=300)


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    type: str
    title: str
    original_uri: str | None
    status: str
    metadata: dict
    char_count: int | None = None
    preview: str | None = None
    created_at: datetime
    updated_at: datetime


def require_project(db: Session, project_id: uuid.UUID) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.status == "deleted":
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def source_out(db: Session, source: Source, include_text: bool = False) -> SourceOut:
    document = db.scalar(select(SourceDocument).where(SourceDocument.source_id == source.id))
    preview = None
    if document and document.text:
        preview = document.text if include_text else document.text[:500]
    return SourceOut(
        id=source.id,
        project_id=source.project_id,
        type=source.type,
        title=source.title,
        original_uri=source.original_uri,
        status=source.status,
        metadata=source.metadata_json,
        char_count=document.char_count if document else None,
        preview=preview,
        created_at=source.created_at,
        updated_at=source.updated_at,
    )


@router.post(
    "/projects/{project_id}/sources/text",
    response_model=SourceOut,
    status_code=status.HTTP_201_CREATED,
)
def add_text_source(project_id: uuid.UUID, body: TextSourceCreate, db: DbSession) -> SourceOut:
    require_project(db, project_id)
    source_type = "markdown" if body.format == "markdown" else "text"
    source = Source(project_id=project_id, type=source_type, title=body.title)
    db.add(source)
    db.flush()
    source.blob_path = get_blob_store().put(
        f"uploads/{source.id}/source.{'md' if source_type == 'markdown' else 'txt'}",
        body.text.encode(),
    )
    db.commit()
    process_source(db, source)
    db.refresh(source)
    return source_out(db, source)


@router.post(
    "/projects/{project_id}/sources/upload",
    response_model=SourceOut,
    status_code=status.HTTP_201_CREATED,
)
def upload_source(
    project_id: uuid.UUID,
    db: DbSession,
    file: Annotated[UploadFile, File()],
    title: Annotated[str | None, Form()] = None,
) -> SourceOut:
    require_project(db, project_id)
    suffix = (file.filename or "").lower()
    if suffix.endswith(".pdf"):
        source_type = "pdf"
    elif suffix.endswith((".md", ".markdown")):
        source_type = "markdown"
    elif suffix.endswith(".txt"):
        source_type = "txt"
    else:
        raise HTTPException(
            status_code=415, detail="Only TXT, Markdown, and PDF files are supported"
        )
    try:
        safe_name = safe_upload_name(file.filename, source_type)
    except SourceExtractionError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    content = file.file.read(get_settings().max_upload_bytes + 1)
    if len(content) > get_settings().max_upload_bytes:
        raise HTTPException(status_code=413, detail="The upload exceeds the configured size limit")
    source = Source(
        project_id=project_id,
        type=source_type,
        title=(title or file.filename or "Uploaded source")[:300],
        metadata_json={"original_filename": file.filename, "content_type": file.content_type},
    )
    db.add(source)
    db.flush()
    source.blob_path = get_blob_store().put(f"uploads/{source.id}/{safe_name}", content)
    db.commit()
    process_source(db, source)
    db.refresh(source)
    return source_out(db, source)


@router.post(
    "/projects/{project_id}/sources/url",
    response_model=SourceOut,
    status_code=status.HTTP_201_CREATED,
)
def add_url_source(project_id: uuid.UUID, body: URLSourceCreate, db: DbSession) -> SourceOut:
    require_project(db, project_id)
    url = str(body.url)
    source = Source(
        project_id=project_id,
        type="url",
        title=body.title or body.url.host or "Web source",
        original_uri=url,
    )
    db.add(source)
    db.commit()
    process_source(db, source)
    db.refresh(source)
    return source_out(db, source)


@router.get("/projects/{project_id}/sources", response_model=list[SourceOut])
def list_sources(project_id: uuid.UUID, db: DbSession) -> list[SourceOut]:
    require_project(db, project_id)
    sources = db.scalars(
        select(Source).where(Source.project_id == project_id).order_by(Source.created_at.desc())
    )
    return [source_out(db, source) for source in sources]


@router.get("/sources/{source_id}", response_model=SourceOut)
def get_source(source_id: uuid.UUID, db: DbSession) -> SourceOut:
    source = db.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source_out(db, source, include_text=True)


@router.post("/sources/{source_id}/reprocess", response_model=SourceOut)
def reprocess_source(source_id: uuid.UUID, db: DbSession) -> SourceOut:
    source = db.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    process_source(db, source)
    db.refresh(source)
    return source_out(db, source)


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id: uuid.UUID, db: DbSession) -> None:
    source = db.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    if source.blob_path:
        get_blob_store().delete(source.blob_path)
    db.delete(source)
    db.commit()
