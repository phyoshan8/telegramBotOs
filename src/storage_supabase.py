from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from supabase import create_client, Client

from .config import Settings
from .storage import Storage


class SupabaseStorage(Storage):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be provided")
        self.client: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)

    def _now(self) -> datetime:
        return datetime.now(ZoneInfo(self.settings.timezone))

    def _to_sheet_format(self, record: dict) -> dict[str, str]:
        return {
            "ID": record.get("order_code") or "",
            "Date": record.get("order_date") or "",
            "Customer Name": record.get("customer_name") or "",
            "Phone": record.get("phone") or "",
            "Item": record.get("item") or "",
            "Size": record.get("size") or "-",
            "Color": record.get("color") or "-",
            "Quantity": str(record.get("quantity") or "1"),
            "Amount": str(record.get("amount") or "0"),
            "Payment Status": record.get("payment_status") or "",
            "Payment Method": record.get("payment_method") or "-",
            "Delivery Status": record.get("delivery_status") or "",
            "Address/Note": record.get("address_note") or "-",
            "Status": record.get("status") or "Open",
            "Created At": record.get("created_at") or "",
            "Updated At": record.get("updated_at") or "",
        }

    def setup(self) -> None:
        # Tables and database structure are initialized via supabase/schema.sql,
        # so nothing is required to run dynamically at start.
        pass

    def append_order(self, order: dict[str, str]) -> dict[str, str]:
        now = self._now()
        
        # Parse fields to correct types to match postgres schema
        try:
            quantity = int(float(str(order.get("Quantity", "1")).replace(",", "").strip() or 1))
        except ValueError:
            quantity = 1

        try:
            amount = int(float(str(order.get("Amount", "0")).replace(",", "").strip() or 0))
        except ValueError:
            amount = 0

        row_data = {
            "order_date": now.strftime("%Y-%m-%d"),
            "customer_name": order.get("Customer Name", "").strip(),
            "phone": order.get("Phone", "").strip(),
            "item": order.get("Item", "").strip(),
            "size": order.get("Size", "").strip() or None,
            "color": order.get("Color", "").strip() or None,
            "quantity": quantity,
            "amount": amount,
            "payment_status": order.get("Payment Status", "").strip(),
            "payment_method": order.get("Payment Method", "").strip() or None,
            "delivery_status": order.get("Delivery Status", "").strip(),
            "address_note": order.get("Address/Note", "").strip() or None,
            "status": order.get("Status", "Open").strip() or "Open"
        }

        res = self.client.table("orders").insert(row_data).execute()
        
        if not res.data:
            raise RuntimeError("Failed to save order to Supabase")
            
        return self._to_sheet_format(res.data[0])

    def unpaid_orders(self) -> list[dict[str, str]]:
        res = self.client.table("orders") \
            .select("*") \
            .eq("status", "Open") \
            .in_("payment_status", ["Unpaid", "COD", "Deposit"]) \
            .order("id") \
            .execute()
        return [self._to_sheet_format(row) for row in res.data]

    def pending_delivery_orders(self) -> list[dict[str, str]]:
        res = self.client.table("orders") \
            .select("*") \
            .eq("status", "Open") \
            .eq("delivery_status", "Pending") \
            .order("id") \
            .execute()
        return [self._to_sheet_format(row) for row in res.data]

    def today_report(self) -> dict[str, int]:
        today = self._now().strftime("%Y-%m-%d")
        res = self.client.table("orders") \
            .select("*") \
            .eq("order_date", today) \
            .execute()
        
        orders = res.data
        total_amount = sum(row.get("amount") or 0 for row in orders)
        unpaid = [row for row in orders if row.get("payment_status") in {"Unpaid", "COD", "Deposit"}]
        pending = [row for row in orders if row.get("delivery_status") == "Pending"]

        return {
            "total_orders": len(orders),
            "total_amount": total_amount,
            "unpaid_amount": sum(row.get("amount") or 0 for row in unpaid),
            "unpaid_count": len(unpaid),
            "pending_count": len(pending),
        }

    def get_user_language(self, telegram_user_id: int) -> str | None:
        res = self.client.table("user_settings") \
            .select("language") \
            .eq("telegram_user_id", telegram_user_id) \
            .execute()
        
        if res.data:
            lang = str(res.data[0].get("language", "")).strip()
            return lang if lang in {"en", "my"} else None
        return None

    def set_user_language(
        self,
        telegram_user_id: int,
        username: str | None,
        first_name: str | None,
        language: str,
    ) -> None:
        if language not in {"en", "my"}:
            raise ValueError("language must be 'en' or 'my'")

        row_data = {
            "telegram_user_id": telegram_user_id,
            "username": username or None,
            "first_name": first_name or None,
            "language": language,
            "updated_at": self._now().isoformat()
        }

        self.client.table("user_settings") \
            .upsert(row_data, on_conflict="telegram_user_id") \
            .execute()
