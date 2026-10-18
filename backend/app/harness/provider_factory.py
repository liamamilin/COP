"""Provider resolution for a run.

The backend owns the settings merge. Precedence is fixed by the consistency
contract: run override > project setting > app setting > built-in default.
"""

from typing import Any

from app.api.settings import deep_merge, settings_with_defaults
from app.core.config import get_settings
from app.core.errors import CopStudioError
from app.db.models import AppSetting, Project, ProjectSettings
from app.harness.providers import MockProvider, OpenAICompatibleProvider, ProviderError
from app.harness.providers.base import LLMProvider


def resolve_effective_settings(db, project_id: Any) -> dict[str, Any]:
    """Merge app defaults with project overrides.

    `projects.preferred_language` participates as a project-level source. It is a
    first-class column rather than a settings row, and the audit found it was
    written at creation and then never read: a project created in Chinese
    generated an English COP unless the user re-selected the language by hand.
    It only fills in when no explicit project override says otherwise, so a
    deliberate override still wins over it.
    """
    app_record = db.get(AppSetting, 1)
    app_data = app_record.settings_json if app_record else {}
    project_record = db.get(ProjectSettings, project_id)
    project_data = dict(project_record.settings_json) if project_record else {}

    project_row = db.get(Project, project_id)
    preferred = str(getattr(project_row, "preferred_language", "") or "").strip()
    if preferred and preferred != "auto":
        existing = dict(project_data.get("generation") or {})
        existing.setdefault("language", preferred)
        project_data["generation"] = existing

    return deep_merge(settings_with_defaults(app_data), project_data)


def resolve_effective_settings_with_run(
    db, project_id: Any, run_override: dict[str, Any] | None
) -> dict[str, Any]:
    effective = resolve_effective_settings(db, project_id)
    if run_override:
        effective = deep_merge(effective, run_override)
    return effective


def _decrypt_provider(db, provider: dict[str, Any]) -> dict[str, Any]:
    """Attach the plaintext key for internal use only."""
    from app.core.security import get_secret_cipher

    config = get_settings()
    ciphertext = provider.get("api_key_ciphertext")
    api_key = get_secret_cipher().decrypt(ciphertext) if ciphertext else ""
    base_url = str(provider.get("base_url") or "").rstrip("/")
    env_base_url = config.openai_compatible_base_url.rstrip("/")
    if provider.get("type") == "openai_compatible" and base_url == env_base_url and not api_key:
        api_key = config.openai_compatible_api_key
    return {**provider, "api_key": api_key}


def build_provider(db, project_id: Any, run_override: dict[str, Any] | None = None) -> LLMProvider:
    """Construct the provider adapter for a run, or explain why it cannot run."""
    effective = resolve_effective_settings_with_run(db, project_id, run_override)
    provider = _decrypt_provider(db, effective.get("provider") or {})

    if provider.get("type") == "mock":
        return MockProvider(provider.get("mock_scenario", "success"))

    missing = [
        field
        for field in ("base_url", "api_key", "model")
        if not str(provider.get(field) or "").strip()
    ]
    if missing:
        raise CopStudioError(
            "PROVIDER_NOT_CONFIGURED",
            f"Generation cannot start: provider is missing {', '.join(missing)}",
            status_code=422,
        )
    return OpenAICompatibleProvider(
        base_url=provider["base_url"],
        api_key=provider["api_key"],
        model=provider["model"],
        timeout=float(provider.get("timeout") or 60),
        max_retries=int(provider.get("max_retries", 2)),
    )


__all__ = [
    "ProviderError",
    "build_provider",
    "resolve_effective_settings",
    "resolve_effective_settings_with_run",
]
