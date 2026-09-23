from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-terra"
    openai_timeout_seconds: float = Field(default=45, ge=1, le=120)
    database_url: str = "sqlite:///./data/gyver.db"
    upload_dir: Path = Path("uploads")
    max_upload_mb: int = Field(default=8, ge=1, le=30)


@lru_cache
def get_settings() -> Settings:
    return Settings()
