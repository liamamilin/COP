import uuid
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_secret_cipher, secret_hint
from app.db.models import AppSetting, Project, ProjectSettings
from app.db.session import get_db
from app.harness.providers import MockProvider, OpenAICompatibleProvider, ProviderError

router = APIRouter(tags=["settings"])
DbSession = Annotated[Session, Depends(get_db)]

BUILT_IN_DEFAULTS: dict[str, Any] = {
    "provider": {
        "type": "mock",
        "base_url": "",
        "model": "",
        "timeout": 60,
        "max_retries": 2,
        "mock_scenario": "success",
    },
    "generation": {
        "language": "auto",
        "generation_depth": "standard",
        "learner_level": "new",
        "detail_density": "balanced",
        "practice_mode": "priority",
        "evidence_density": "key_claims",
    },
    "appearance": {"theme": "system", "density": "comfortable"},
}


class ProviderUpdate(BaseModel):
    type: Literal["mock", "openai_compatible"] = "mock"
    base_url: str = ""
    api_key: str | None = None
    clear_api_key: bool = False
    model: str = ""
    timeout: int = Field(default=60, ge=5, le=600)
    max_retries: int = Field(default=2, ge=0, le=5)
    mock_scenario: Literal["success", "invalid", "timeout", "rate_limit", "slow"] = "success"


class SettingsUpdate(BaseModel):
    provider: ProviderUpdate | None = None
    generation: dict[str, Any] | None = None
    appearance: dict[str, Any] | None = None


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def app_record(db: Session) -> AppSetting:
    record = db.get(AppSetting, 1)
    if record is None:
        record = AppSetting(id=1, settings_json={})
        db.add(record)
        db.flush()
    return record


def settings_with_defaults(data: dict[str, Any]) -> dict[str, Any]:
    """Apply built-in and environment defaults without removing stored secrets."""
    merged = deep_merge(BUILT_IN_DEFAULTS, data)
    config = get_settings()
    if not data.get("provider") and config.cop_provider_mode == "openai_compatible":
        merged["provider"] = {
            **merged["provider"],
            "type": "openai_compatible",
            "base_url": config.openai_compatible_base_url,
            "model": config.openai_compatible_model,
        }
    return merged


def public_settings(data: dict[str, Any]) -> dict[str, Any]:
    merged = settings_with_defaults(data)
    config = get_settings()
    provider = dict(merged["provider"])
    provider.pop("api_key_ciphertext", None)
    provider.pop("api_key", None)
    provider.pop("clear_api_key", None)
    provider["has_api_key"] = bool(data.get("provider", {}).get("api_key_ciphertext"))
    if provider.get("type") == "openai_compatible":
        base_url = str(provider.get("base_url") or "").rstrip("/")
        env_base_url = config.openai_compatible_base_url.rstrip("/")
        provider["has_api_key"] = provider["has_api_key"] or bool(
            config.openai_compatible_api_key and base_url == env_base_url
        )
    provider["api_key_hint"] = data.get("provider", {}).get("api_key_hint")
    merged["provider"] = provider
    merged.pop("worker", None)
    return merged


def resolved_private_settings(data: dict[str, Any]) -> dict[str, Any]:
    merged = settings_with_defaults(data)
    provider = dict(merged["provider"])
    ciphertext = provider.get("api_key_ciphertext")
    api_key = get_secret_cipher().decrypt(ciphertext) if ciphertext else ""
    config = get_settings()
    base_url = str(provider.get("base_url") or "").rstrip("/")
    env_base_url = config.openai_compatible_base_url.rstrip("/")
    if provider.get("type") == "openai_compatible" and base_url == env_base_url and not api_key:
        api_key = config.openai_compatible_api_key
    provider["api_key"] = api_key
    merged["provider"] = provider
    return merged


@router.get("/settings")
def get_app_settings(db: DbSession) -> dict[str, Any]:
    return public_settings(app_record(db).settings_json)


@router.patch("/settings")
def update_app_settings(body: SettingsUpdate, db: DbSession) -> dict[str, Any]:
    record = app_record(db)
    existing = record.settings_json
    patch = body.model_dump(exclude_none=True)
    provider_update = patch.get("provider")
    if provider_update is not None:
        api_key = provider_update.pop("api_key", None)
        clear_api_key = provider_update.pop("clear_api_key", False)
        current_provider = dict(existing.get("provider", {}))
        if clear_api_key:
            current_provider.pop("api_key_ciphertext", None)
            current_provider.pop("api_key_hint", None)
        elif api_key:
            current_provider["api_key_ciphertext"] = get_secret_cipher().encrypt(api_key)
            current_provider["api_key_hint"] = secret_hint(api_key)
        patch["provider"] = {**current_provider, **provider_update}
    updated = deep_merge(existing, patch)
    if provider_update is not None:
        updated["provider"] = patch["provider"]
    record.settings_json = updated
    db.commit()
    db.refresh(record)
    return public_settings(record.settings_json)


@router.post("/settings/provider/test")
async def test_provider(db: DbSession) -> dict[str, Any]:
    provider = resolved_private_settings(app_record(db).settings_json)["provider"]
    if provider["type"] == "mock":
        adapter = MockProvider(provider.get("mock_scenario", "success"))
    else:
        if not provider.get("base_url") or not provider.get("api_key") or not provider.get("model"):
            raise HTTPException(status_code=422, detail="Base URL, API key, and model are required")
        adapter = OpenAICompatibleProvider(
            base_url=provider["base_url"],
            api_key=provider["api_key"],
            model=provider["model"],
            timeout=provider["timeout"],
            max_retries=provider["max_retries"],
        )
    try:
        return await adapter.health_check()
    except ProviderError as exc:
        raise HTTPException(
            status_code=400, detail={"code": exc.code, "message": str(exc)}
        ) from exc


@router.get("/projects/{project_id}/settings")
def get_project_settings(project_id: uuid.UUID, db: DbSession) -> dict[str, Any]:
    if db.get(Project, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    project = db.get(ProjectSettings, project_id)
    project_data = project.settings_json if project else {}
    app_data = app_record(db).settings_json
    effective = deep_merge(public_settings(app_data), project_data)
    return {"overrides": project_data, "effective": effective}


@router.patch("/projects/{project_id}/settings")
def update_project_settings(
    project_id: uuid.UUID, body: dict[str, Any], db: DbSession
) -> dict[str, Any]:
    if db.get(Project, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    record = db.get(ProjectSettings, project_id)
    if record is None:
        record = ProjectSettings(project_id=project_id, settings_json={})
        db.add(record)
    record.settings_json = deep_merge(record.settings_json, body)
    db.commit()
    return get_project_settings(project_id, db)
