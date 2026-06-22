from __future__ import annotations


class AdminService:
    def __init__(self, storage) -> None:
        self.storage = storage

    def today_report(self) -> dict[str, int]:
        return self.storage.today_report()

    def unpaid_orders(self) -> list[dict[str, str]]:
        return self.storage.unpaid_orders()

    def pending_delivery_orders(self) -> list[dict[str, str]]:
        return self.storage.pending_delivery_orders()
