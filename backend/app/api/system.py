from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import AppSetting
from app.db.session import get_db

router = APIRouter(tags=["system"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/system/worker")
def worker_status(db: DbSession) -> dict[str, Any]:
    settings = db.get(AppSetting, 1)
    worker = settings.settings_json.get("worker") if settings else None
    if not worker:
        raise HTTPException(status_code=503, detail="No worker heartbeat has been recorded")
    return {"status": "ok", **worker}
