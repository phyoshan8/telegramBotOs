from __future__ import annotations


class AdminService:
    def __init__(self, storage) -> None:
        self.storage = storage

    def is_admin_user(self, telegram_user_id: int) -> bool:
        get_user_role = getattr(self.storage, "get_user_role", None)
        if not callable(get_user_role):
            return False
        return str(get_user_role(telegram_user_id) or "").strip().lower() == "admin"

    def today_report(self) -> dict[str, int]:
        return self.storage.today_report()

    def unpaid_orders(self) -> list[dict[str, str]]:
        return self.storage.unpaid_orders()

    def pending_delivery_orders(self) -> list[dict[str, str]]:
        return self.storage.pending_delivery_orders()
