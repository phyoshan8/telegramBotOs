from pathlib import Path

from src.config import Settings
from src.storage_factory import build_storage


def test_build_storage_returns_sheets_backend_for_sheets_settings(tmp_path):
    settings = Settings(
        telegram_bot_token="token",
        storage_backend="sheets",
        google_sheet_id="sheet-id",
        google_service_account_file=tmp_path / "service.json",
        google_sheet_tab="Orders",
        timezone="Asia/Yangon",
    )

    storage = build_storage(settings)

    assert storage.__class__.__name__ == "GoogleSheetsStorage"
