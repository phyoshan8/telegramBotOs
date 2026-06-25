from pathlib import Path

from src.config import Settings
from src.storage_supabase import SupabaseStorage


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, table_name, client):
        self.table_name = table_name
        self.client = client
        self.filters = []
        self.order_by = None
        self.insert_payload = None
        self.upsert_payload = None

    def select(self, _fields):
        return self

    def eq(self, field, value):
        self.filters.append(("eq", field, value))
        return self

    def in_(self, field, values):
        self.filters.append(("in", field, tuple(values)))
        return self

    def order(self, field):
        self.order_by = field
        return self

    def insert(self, payload):
        self.insert_payload = payload
        self.client.last_insert = (self.table_name, payload)
        return self

    def upsert(self, payload, on_conflict=None):
        self.upsert_payload = (payload, on_conflict)
        self.client.last_upsert = (self.table_name, payload, on_conflict)
        return self

    def execute(self):
        if self.insert_payload is not None:
            inserted = {
                "order_code": "C-0001",
                **self.insert_payload,
                "created_at": "2026-06-24T10:00:00+06:30",
                "updated_at": "2026-06-24T10:00:00+06:30",
            }
            return FakeResponse([inserted])
        if self.upsert_payload is not None:
            return FakeResponse([self.upsert_payload[0]])

        data = list(self.client.tables[self.table_name])
        for filter_type, field, value in self.filters:
            if filter_type == "eq":
                data = [row for row in data if row.get(field) == value]
            elif filter_type == "in":
                data = [row for row in data if row.get(field) in value]
        if self.order_by is not None:
            data.sort(key=lambda row: row.get(self.order_by))
        return FakeResponse(data)


class FakeSupabaseClient:
    def __init__(self):
        self.tables = {
            "orders": [
                {
                    "id": 2,
                    "order_code": "C-0002",
                    "order_date": "2026-06-24",
                    "customer_name": "Hla",
                    "phone": "09222",
                    "item": "Skirt",
                    "size": "M",
                    "color": "Blue",
                    "quantity": 1,
                    "amount": 12000,
                    "payment_status": "Paid",
                    "payment_method": "KBZPay",
                    "delivery_status": "Pending",
                    "address_note": "Downtown",
                    "status": "Open",
                    "created_at": "2026-06-24T09:00:00+06:30",
                    "updated_at": "2026-06-24T09:00:00+06:30",
                },
                {
                    "id": 1,
                    "order_code": "C-0001",
                    "order_date": "2026-06-24",
                    "customer_name": "Aye",
                    "phone": "09111",
                    "item": "Shirt",
                    "size": "L",
                    "color": "Red",
                    "quantity": 2,
                    "amount": 15000,
                    "payment_status": "Unpaid",
                    "payment_method": None,
                    "delivery_status": "Pending",
                    "address_note": None,
                    "status": "Open",
                    "created_at": "2026-06-24T08:00:00+06:30",
                    "updated_at": "2026-06-24T08:00:00+06:30",
                },
                {
                    "id": 3,
                    "order_code": "C-0003",
                    "order_date": "2026-06-23",
                    "customer_name": "Mya",
                    "phone": "09333",
                    "item": "Bag",
                    "size": None,
                    "color": None,
                    "quantity": 1,
                    "amount": 5000,
                    "payment_status": "Deposit",
                    "payment_method": None,
                    "delivery_status": "Delivered",
                    "address_note": None,
                    "status": "Closed",
                    "created_at": "2026-06-23T08:00:00+06:30",
                    "updated_at": "2026-06-23T08:00:00+06:30",
                },
            ],
            "user_settings": [
                {"telegram_user_id": 100, "language": "en", "role": "admin"},
                {"telegram_user_id": 200, "language": "my", "role": "seller"},
            ],
        }
        self.last_insert = None
        self.last_upsert = None

    def table(self, table_name):
        return FakeQuery(table_name, self)


def _settings() -> Settings:
    return Settings(
        telegram_bot_token="token",
        storage_backend="supabase",
        google_sheet_id="",
        google_service_account_file=Path(),
        google_sheet_tab="Orders",
        timezone="Asia/Yangon",
        supabase_url="https://example.supabase.co",
        supabase_service_role_key="service-role",
    )


def test_append_order_inserts_and_returns_sheet_format():
    client = FakeSupabaseClient()
    storage = SupabaseStorage(_settings(), client=client)

    saved = storage.append_order(
        {
            "Customer Name": "Aye",
            "Phone": "09123",
            "Item": "Shirt",
            "Quantity": "2",
            "Amount": "15000",
            "Payment Status": "Unpaid",
            "Delivery Status": "Pending",
        }
    )

    assert client.last_insert[0] == "orders"
    assert client.last_insert[1]["quantity"] == 2
    assert client.last_insert[1]["amount"] == 15000
    assert saved["ID"] == "C-0001"
    assert saved["Customer Name"] == "Aye"
    assert saved["Quantity"] == "2"
    assert saved["Amount"] == "15000"


def test_unpaid_orders_returns_only_open_unpaid_rows():
    storage = SupabaseStorage(_settings(), client=FakeSupabaseClient())

    rows = storage.unpaid_orders()

    assert [row["ID"] for row in rows] == ["C-0001"]


def test_pending_delivery_orders_returns_open_pending_rows_in_id_order():
    storage = SupabaseStorage(_settings(), client=FakeSupabaseClient())

    rows = storage.pending_delivery_orders()

    assert [row["ID"] for row in rows] == ["C-0001", "C-0002"]


def test_today_report_aggregates_counts_and_amounts():
    storage = SupabaseStorage(_settings(), client=FakeSupabaseClient())

    report = storage.today_report()

    assert report == {
        "total_orders": 2,
        "total_amount": 27000,
        "unpaid_amount": 15000,
        "unpaid_count": 1,
        "pending_count": 2,
    }


def test_get_user_language_returns_supported_language_only():
    storage = SupabaseStorage(_settings(), client=FakeSupabaseClient())

    assert storage.get_user_language(100) == "en"
    assert storage.get_user_language(999) is None


def test_get_user_role_returns_normalized_role_when_present():
    storage = SupabaseStorage(_settings(), client=FakeSupabaseClient())

    assert storage.get_user_role(100) == "admin"
    assert storage.get_user_role(200) == "seller"


def test_get_user_role_returns_none_when_missing_or_blank():
    client = FakeSupabaseClient()
    client.tables["user_settings"].append({"telegram_user_id": 300, "language": "en", "role": "   "})
    storage = SupabaseStorage(_settings(), client=client)

    assert storage.get_user_role(300) is None
    assert storage.get_user_role(999) is None


def test_set_user_language_upserts_supported_language():
    client = FakeSupabaseClient()
    storage = SupabaseStorage(_settings(), client=client)

    storage.set_user_language(123, "aye", "Aye", "my")

    assert client.last_upsert[0] == "user_settings"
    assert client.last_upsert[1]["telegram_user_id"] == 123
    assert client.last_upsert[1]["language"] == "my"
    assert client.last_upsert[2] == "telegram_user_id"


def test_list_all_orders_returns_sheet_format_rows_in_id_order():
    storage = SupabaseStorage(_settings(), client=FakeSupabaseClient())

    rows = storage.list_all_orders()

    assert [row["ID"] for row in rows] == ["C-0001", "C-0002", "C-0003"]
