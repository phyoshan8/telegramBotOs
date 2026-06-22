from pathlib import Path

import pytest

from src.config import load_settings


def _clear_env(monkeypatch):
    for key in [
        "TELEGRAM_BOT_TOKEN",
        "STORAGE_BACKEND",
        "GOOGLE_SHEET_ID",
        "GOOGLE_SERVICE_ACCOUNT_FILE",
        "GOOGLE_SHEET_TAB",
        "TIMEZONE",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)


def test_storage_backend_defaults_to_sheets(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    service_file = tmp_path / "service.json"
    service_file.write_text("{}")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("GOOGLE_SHEET_ID", "sheet-id")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(service_file))

    settings = load_settings()

    assert settings.storage_backend == "sheets"
    assert settings.google_sheet_id == "sheet-id"


def test_invalid_storage_backend_raises(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    service_file = tmp_path / "service.json"
    service_file.write_text("{}")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("GOOGLE_SHEET_ID", "sheet-id")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(service_file))
    monkeypatch.setenv("STORAGE_BACKEND", "unknown")

    with pytest.raises(RuntimeError, match="STORAGE_BACKEND"):
        load_settings()


def test_supabase_backend_requires_only_supabase_settings(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("STORAGE_BACKEND", "supabase")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role")

    settings = load_settings()

    assert settings.storage_backend == "supabase"
    assert settings.supabase_url == "https://example.supabase.co"
    assert settings.supabase_service_role_key == "service-role"
