"""Application settings, read from PRACTICE_* environment variables or a .env file."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PRACTICE_", env_file=".env", extra="ignore")

    app_name: str = "edge-app-practice"
    db_path: str = "data/practice.db"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
