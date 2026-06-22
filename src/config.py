from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    storage_backend: str
    google_sheet_id: str
    google_service_account_file: Path
    google_sheet_tab: str
    timezone: str
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None


def load_settings() -> Settings:
    """Load secrets/config from .env.

    Logic: the bot code must not contain tokens or client-specific Sheet IDs.
    .env is the private config file. Code stays reusable for future clients.
    """
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    storage_backend = os.getenv("STORAGE_BACKEND", "sheets").strip().lower() or "sheets"
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "").strip()
    service_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "").strip()
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing in .env")
    if storage_backend not in {"sheets", "supabase"}:
        raise RuntimeError("STORAGE_BACKEND must be 'sheets' or 'supabase'")

    service_path = Path(service_file).expanduser() if service_file else Path()

    if storage_backend == "sheets":
        if not sheet_id:
            raise RuntimeError("GOOGLE_SHEET_ID is missing in .env")
        if not service_file:
            raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_FILE is missing in .env")
        if not service_path.exists():
            raise RuntimeError(f"Google service account file not found: {service_path}")
    else:
        if not supabase_url:
            raise RuntimeError("SUPABASE_URL is missing in .env")
        if not supabase_service_role_key:
            raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is missing in .env")

    return Settings(
        telegram_bot_token=token,
        storage_backend=storage_backend,
        google_sheet_id=sheet_id,
        google_service_account_file=service_path,
        google_sheet_tab=os.getenv("GOOGLE_SHEET_TAB", "Orders").strip() or "Orders",
        timezone=os.getenv("TIMEZONE", "Asia/Yangon").strip() or "Asia/Yangon",
        supabase_url=supabase_url or None,
        supabase_service_role_key=supabase_service_role_key or None,
    )
