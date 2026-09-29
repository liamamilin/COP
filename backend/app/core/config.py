from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_secret: str = "development-only-change-me"
    database_url: str = "postgresql+psycopg://cop:cop@localhost:5432/cop"
    data_dir: Path = Path("./data")
    log_level: str = "INFO"
    web_origin: str = "http://localhost:3000"
    cop_provider_mode: str = "mock"
    openai_compatible_base_url: str = ""
    openai_compatible_api_key: str = ""
    openai_compatible_model: str = ""
    exa_api_key: str = ""
    exa_base_url: str = "https://api.exa.ai"
    exa_num_results: int = 5
    worker_poll_seconds: float = 2.0
    max_upload_bytes: int = 20 * 1024 * 1024
    url_timeout_seconds: float = 15.0

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
