from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MirroredStorage:
    def __init__(self, primary: Any, mirror: Any) -> None:
        self.primary = primary
        self.mirror = mirror

    def setup(self) -> None:
        self.primary.setup()
        self.mirror.setup()

    def append_order(self, order: dict[str, str]) -> dict[str, str]:
        saved = self.primary.append_order(order)
        try:
            self.mirror.export_order(saved)
        except Exception:
            logger.exception("Google Sheets export failed after Supabase save")
        return saved

    def unpaid_orders(self) -> list[dict[str, str]]:
        return self.primary.unpaid_orders()

    def pending_delivery_orders(self) -> list[dict[str, str]]:
        return self.primary.pending_delivery_orders()

    def today_report(self) -> dict[str, int]:
        return self.primary.today_report()

    def get_user_language(self, telegram_user_id: int) -> str | None:
        return self.primary.get_user_language(telegram_user_id)

    def get_user_role(self, telegram_user_id: int) -> str | None:
        return self.primary.get_user_role(telegram_user_id)

    def set_user_language(
        self,
        telegram_user_id: int,
        username: str | None,
        first_name: str | None,
        language: str,
    ) -> None:
        self.primary.set_user_language(telegram_user_id, username, first_name, language)
