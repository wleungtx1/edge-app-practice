from pathlib import Path

import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings


def test_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PRACTICE_DB_PATH")

    settings = Settings()

    assert settings.app_name == "edge-app-practice"
    assert settings.db_path == "data/practice.db"
    assert settings.log_level == "INFO"


def test_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PRACTICE_APP_NAME", "renamed")
    monkeypatch.setenv("PRACTICE_LOG_LEVEL", "DEBUG")

    settings = Settings()

    assert settings.app_name == "renamed"
    assert settings.log_level == "DEBUG"


def test_env_file_is_read(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("PRACTICE_APP_NAME=from-dotenv\n", encoding="utf-8")

    assert Settings().app_name == "from-dotenv"


def test_invalid_log_level_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PRACTICE_LOG_LEVEL", "LOUD")

    with pytest.raises(ValidationError):
        Settings()


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()
