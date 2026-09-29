"""Export immutable COP versions as portable files."""

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import NotFoundError
from app.db.models import COPVersion
from app.db.session import get_db
from app.domain.exports import json_export, markdown_bundle, markdown_export, safe_slug

router = APIRouter(tags=["exports"])
DbSession = Annotated[Session, Depends(get_db)]


class ExportRequest(BaseModel):
    format: Literal["json", "markdown", "markdown_bundle"]


@router.post("/versions/{version_id}/exports", response_class=FileResponse)
def export_version(version_id: uuid.UUID, body: ExportRequest, db: DbSession) -> FileResponse:
    version = db.get(COPVersion, version_id)
    if version is None:
        raise NotFoundError("Version not found", code="VERSION_NOT_FOUND")

    artifact = version.artifact_json
    base = safe_slug(str((artifact.get("domain") or {}).get("name") or "cop"))
    output_dir = get_settings().data_dir / "exports" / str(version.id)
    output_dir.mkdir(parents=True, exist_ok=True)

    if body.format == "json":
        filename = f"{base}-v{version.version_number}.json"
        media_type = "application/json"
        content = json_export(artifact)
    elif body.format == "markdown":
        filename = f"{base}-v{version.version_number}.md"
        media_type = "text/markdown; charset=utf-8"
        content = markdown_export(artifact, version_number=version.version_number).encode()
    else:
        filename = f"{base}-v{version.version_number}-markdown.zip"
        media_type = "application/zip"
        content = markdown_bundle(artifact, version_number=version.version_number)

    path = output_dir / filename
    path.write_bytes(content)
    return FileResponse(path, media_type=media_type, filename=filename)
