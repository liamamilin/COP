from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.generations import router as generations_router
from app.api.projects import router as projects_router
from app.api.settings import router as settings_router
from app.api.sources import router as sources_router
from app.api.system import router as system_router
from app.core.config import get_settings
from app.core.errors import CopStudioError, error_response
from app.db.session import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    for directory in ("uploads", "extracted", "exports"):
        (settings.data_dir / directory).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="COP Studio API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(projects_router, prefix="/api/v1")
app.include_router(generations_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(sources_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")


@app.exception_handler(CopStudioError)
async def cop_studio_error_handler(_: Request, exc: CopStudioError) -> JSONResponse:
    """Render domain errors in the documented envelope so codes stay stable."""
    return error_response(exc)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "api"}


@app.get("/ready")
def ready() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable") from exc
    return {"status": "ready", "database": "ok"}
