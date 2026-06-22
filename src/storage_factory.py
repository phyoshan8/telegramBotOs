from __future__ import annotations

from .config import Settings
from .storage import Storage
from .storage_sheets import GoogleSheetsStorage
from .storage_supabase import SupabaseStorage


def build_storage(settings: Settings) -> Storage:
    if settings.storage_backend == "sheets":
        return GoogleSheetsStorage(settings)
    if settings.storage_backend == "supabase":
        return SupabaseStorage(settings)

    raise RuntimeError(f"Unsupported storage backend: {settings.storage_backend}")
