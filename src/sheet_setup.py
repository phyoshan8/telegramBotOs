from __future__ import annotations

from .config import load_settings
from .storage_sheets import setup_sheet


def main() -> None:
    settings = load_settings()
    setup_sheet(settings)
    print("Google Sheet initialized")
    print(f"Sheet ID: {settings.google_sheet_id}")
    print(f"Orders tab: {settings.google_sheet_tab}")


if __name__ == "__main__":
    main()
