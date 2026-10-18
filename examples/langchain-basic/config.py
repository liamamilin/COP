"""Explicit tutorial configuration, independent of COP Studio's server secrets."""

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values

ENV_FILE = Path(__file__).resolve().with_name(".env")
DEFAULT_PROMPT = "Answer in one short sentence."


class ConfigError(ValueError):
    """A safe-to-display explanation; never includes a credential's value."""


@dataclass(frozen=True)
class Settings:
    api_key: str = field(repr=False)
    base_url: str
    model: str
    system_prompt: str

    def public_summary(self) -> dict[str, str | bool]:
        return {
            "key_configured": bool(self.api_key),
            "base_url": self.base_url,
            "model": self.model,
            "system_prompt": self.system_prompt,
        }


def load_settings(
    env_file: Path = ENV_FILE,
    environ: Mapping[str, str] | None = None,
) -> Settings:
    """Process LC_* variables win over the .env next to this file, even if blank.

    dotenv_values reads a named file; it does not search parent directories or
    mutate os.environ. Interpolation is disabled so ${NAME} is not hidden input.

    The environ parameter is for test injection only; normal usage should not
    pass it, letting the function read from os.environ directly.
    """
    process = os.environ if environ is None else environ
    saved = dotenv_values(env_file, interpolate=False) if env_file.is_file() else {}

    def value(name: str, default: str = "") -> str:
        raw = process[name] if name in process else saved.get(name, default)
        text = (raw or "").strip()
        if not text or text.startswith("replace-") or "${" in text:
            raise ConfigError(f"Set {name} explicitly in LC_* environment variables or {env_file}.")
        return text

    key = value("LC_API_KEY")
    endpoint = value("LC_BASE_URL")
    model = value("LC_MODEL")
    prompt = value("LC_SYSTEM_PROMPT", DEFAULT_PROMPT)
    try:
        url = urlsplit(endpoint)
        _ = url.port
    except ValueError as error:
        raise ConfigError("LC_BASE_URL must be a valid provider base URL.") from error
    if (
        not url.hostname
        or url.username is not None
        or url.password is not None
        or url.query
        or url.fragment
        or url.scheme not in {"https", "http"}
    ):
        raise ConfigError("LC_BASE_URL must not contain credentials, a query, or a fragment.")
    if url.scheme == "http" and url.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ConfigError("Use HTTPS for a remote provider; HTTP is allowed only for localhost.")
    if url.path.rstrip("/").endswith(("/chat/completions", "/responses")):
        raise ConfigError("LC_BASE_URL is the base path, not a chat/completions or responses URL.")
    return Settings(key, endpoint.rstrip("/"), model, prompt)


if __name__ == "__main__":
    try:
        print(json.dumps(load_settings().public_summary(), ensure_ascii=False, indent=2))
    except ConfigError as error:
        raise SystemExit(f"Configuration error: {error}") from None
