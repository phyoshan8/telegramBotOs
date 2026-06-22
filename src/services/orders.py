from __future__ import annotations


class OrderService:
    def __init__(self, storage) -> None:
        self.storage = storage

    def _normalize_number(self, value: str | int | float | None, default: str = "0") -> str:
        text = str(value if value is not None else default).replace(",", "").strip()
        if not text:
            text = default
        return str(int(float(text)))

    def prepare_order(self, order: dict[str, str]) -> dict[str, str]:
        prepared = dict(order)
        prepared["Quantity"] = self._normalize_number(order.get("Quantity", "1"), default="1")
        prepared["Amount"] = self._normalize_number(order.get("Amount", "0"), default="0")
        prepared["Status"] = prepared.get("Status", "Open").strip() or "Open"
        return prepared

    def create_order(self, order: dict[str, str]) -> dict[str, str]:
        return self.storage.append_order(self.prepare_order(order))
