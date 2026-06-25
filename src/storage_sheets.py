from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any

import gspread
from google.oauth2.service_account import Credentials

from .config import Settings

HEADERS = [
    "ID",
    "Date",
    "Customer Name",
    "Phone",
    "Item",
    "Size",
    "Color",
    "Quantity",
    "Amount",
    "Payment Status",
    "Payment Method",
    "Delivery Status",
    "Address/Note",
    "Status",
    "Created At",
    "Updated At",
]

OLD_HEADERS_WITHOUT_QUANTITY = [
    "ID",
    "Date",
    "Customer Name",
    "Phone",
    "Item",
    "Size",
    "Color",
    "Amount",
    "Payment Status",
    "Payment Method",
    "Delivery Status",
    "Address/Note",
    "Status",
    "Created At",
    "Updated At",
]

USER_SETTINGS_TAB = "User Settings"
USER_SETTINGS_HEADERS = ["Telegram User ID", "Username", "First Name", "Language", "Updated At"]
UNPAID_PAYMENT_STATUSES = {"Unpaid", "COD", "Deposit"}
PENDING_DELIVERY_STATUS = "Pending"


def get_client(settings: Settings) -> gspread.Client:
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_file(
        str(settings.google_service_account_file), scopes=scopes
    )
    return gspread.authorize(credentials)


def open_spreadsheet(settings: Settings) -> gspread.Spreadsheet:
    return get_client(settings).open_by_key(settings.google_sheet_id)


def ensure_worksheet(spreadsheet: gspread.Spreadsheet, title: str, rows: int = 1000, cols: int = 20) -> gspread.Worksheet:
    try:
        return spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)


def setup_sheet(settings: Settings) -> None:
    """Create/verify tabs and headers.

    Logic: this is the reusable client setup command. It prepares the Sheet so
    Shann doesn't manually create columns for every new clothing seller.
    """
    spreadsheet = open_spreadsheet(settings)
    orders = ensure_worksheet(spreadsheet, settings.google_sheet_tab)

    first_row = orders.row_values(1)
    if first_row == OLD_HEADERS_WITHOUT_QUANTITY:
        orders.insert_cols([["Quantity"]], col=8)
    elif first_row != HEADERS:
        orders.update("A1:P1", [HEADERS])
    orders.freeze(rows=1)

    for tab in ["Dashboard", "Unpaid", "Pending Delivery", "Settings"]:
        ensure_worksheet(spreadsheet, tab)

    user_settings = ensure_worksheet(spreadsheet, USER_SETTINGS_TAB)
    if user_settings.row_values(1) != USER_SETTINGS_HEADERS:
        user_settings.update("A1:E1", [USER_SETTINGS_HEADERS])
        user_settings.freeze(rows=1)

    settings_ws = spreadsheet.worksheet("Settings")
    if not settings_ws.get_all_values():
        settings_ws.update(
            "A1:C5",
            [
                ["Setting", "Value", "Notes"],
                ["Shop Name", "", "Client clothing shop name"],
                ["Currency", "MMK", "Myanmar Kyat"],
                ["Timezone", settings.timezone, "Report timezone"],
                ["Bot Type", "Telegram Clothing Order Bot", ""],
            ],
        )
        settings_ws.freeze(rows=1)


def _worksheet(settings: Settings) -> gspread.Worksheet:
    spreadsheet = open_spreadsheet(settings)
    return ensure_worksheet(spreadsheet, settings.google_sheet_tab)


def _user_settings_ws(settings: Settings) -> gspread.Worksheet:
    spreadsheet = open_spreadsheet(settings)
    ws = ensure_worksheet(spreadsheet, USER_SETTINGS_TAB)
    if ws.row_values(1) != USER_SETTINGS_HEADERS:
        ws.update("A1:E1", [USER_SETTINGS_HEADERS])
    return ws


def _now(settings: Settings) -> datetime:
    return datetime.now(ZoneInfo(settings.timezone))


def _parse_amount(value: Any) -> int:
    text = str(value or "").replace(",", "").replace("MMK", "").strip()
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def read_orders(settings: Settings) -> list[dict[str, str]]:
    ws = _worksheet(settings)
    rows = ws.get_all_records()
    return [{str(k): str(v) for k, v in row.items()} for row in rows if row.get("ID")]


def next_order_id(settings: Settings) -> str:
    orders = read_orders(settings)
    return f"C-{len(orders) + 1:04d}"


def append_order(settings: Settings, order: dict[str, str]) -> dict[str, str]:
    ws = _worksheet(settings)
    now = _now(settings)
    order_id = next_order_id(settings)
    row = {
        "ID": order_id,
        "Date": now.strftime("%Y-%m-%d"),
        "Customer Name": order.get("Customer Name", "").strip(),
        "Phone": order.get("Phone", "").strip(),
        "Item": order.get("Item", "").strip(),
        "Size": order.get("Size", "").strip(),
        "Color": order.get("Color", "").strip(),
        "Quantity": str(order.get("Quantity", "")).strip(),
        "Amount": str(_parse_amount(order.get("Amount", "0"))),
        "Payment Status": order.get("Payment Status", "").strip(),
        "Payment Method": order.get("Payment Method", "").strip(),
        "Delivery Status": order.get("Delivery Status", "").strip(),
        "Address/Note": order.get("Address/Note", "").strip(),
        "Status": order.get("Status", "Open").strip() or "Open",
        "Created At": now.isoformat(timespec="seconds"),
        "Updated At": now.isoformat(timespec="seconds"),
    }
    ws.append_row([row[h] for h in HEADERS], value_input_option="USER_ENTERED")
    return row


def unpaid_orders(settings: Settings) -> list[dict[str, str]]:
    return [
        row for row in read_orders(settings)
        if row.get("Status", "Open") == "Open"
        and row.get("Payment Status") in UNPAID_PAYMENT_STATUSES
    ]


def pending_delivery_orders(settings: Settings) -> list[dict[str, str]]:
    return [
        row for row in read_orders(settings)
        if row.get("Status", "Open") == "Open"
        and row.get("Delivery Status") == PENDING_DELIVERY_STATUS
    ]


def today_report(settings: Settings) -> dict[str, int]:
    today = _now(settings).strftime("%Y-%m-%d")
    orders = [row for row in read_orders(settings) if row.get("Date") == today]
    total_amount = sum(_parse_amount(row.get("Amount")) for row in orders)
    unpaid = [row for row in orders if row.get("Payment Status") in UNPAID_PAYMENT_STATUSES]
    pending = [row for row in orders if row.get("Delivery Status") == PENDING_DELIVERY_STATUS]
    return {
        "total_orders": len(orders),
        "total_amount": total_amount,
        "unpaid_amount": sum(_parse_amount(row.get("Amount")) for row in unpaid),
        "unpaid_count": len(unpaid),
        "pending_count": len(pending),
    }


def get_user_language(settings: Settings, telegram_user_id: int) -> str | None:
    ws = _user_settings_ws(settings)
    user_id = str(telegram_user_id)
    for row in ws.get_all_records():
        if str(row.get("Telegram User ID", "")) == user_id:
            lang = str(row.get("Language", "")).strip()
            return lang if lang in {"en", "my"} else None
    return None


def set_user_language(
    settings: Settings,
    telegram_user_id: int,
    username: str | None,
    first_name: str | None,
    language: str,
) -> None:
    if language not in {"en", "my"}:
        raise ValueError("language must be 'en' or 'my'")
    ws = _user_settings_ws(settings)
    user_id = str(telegram_user_id)
    now = _now(settings).isoformat(timespec="seconds")
    values = ws.get_all_values()
    for index, row in enumerate(values[1:], start=2):
        if row and row[0] == user_id:
            ws.update(f"A{index}:E{index}", [[user_id, username or "", first_name or "", language, now]])
            return
    ws.append_row([user_id, username or "", first_name or "", language, now], value_input_option="USER_ENTERED")


class GoogleSheetsExporter:
    def __init__(self, settings: Settings, worksheet: Any | None = None) -> None:
        self.settings = settings
        self._worksheet_override = worksheet

    def setup(self) -> None:
        if self._worksheet_override is None:
            setup_sheet(self.settings)

    def worksheet(self):
        if self._worksheet_override is not None:
            return self._worksheet_override
        return _worksheet(self.settings)

    def export_order(self, row: dict[str, str]) -> None:
        ws = self.worksheet()
        row_values = [row.get(header, "") for header in HEADERS]
        order_id = row.get("ID", "")
        for index, existing in enumerate(ws.get_all_values()[1:], start=2):
            if existing and existing[0] == order_id:
                ws.update(f"A{index}:P{index}", [row_values])
                return
        ws.append_row(row_values, value_input_option="USER_ENTERED")


class GoogleSheetsStorage:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client: gspread.Client | None = None
        self._spreadsheet: gspread.Spreadsheet | None = None
        self._orders_ws: gspread.Worksheet | None = None
        self._user_settings_ws: gspread.Worksheet | None = None

    @property
    def client(self) -> gspread.Client:
        if self._client is None:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            credentials = Credentials.from_service_account_file(
                str(self.settings.google_service_account_file), scopes=scopes
            )
            self._client = gspread.authorize(credentials)
        return self._client

    @property
    def spreadsheet(self) -> gspread.Spreadsheet:
        if self._spreadsheet is None:
            self._spreadsheet = self.client.open_by_key(self.settings.google_sheet_id)
        return self._spreadsheet

    def _get_orders_ws(self) -> gspread.Worksheet:
        if self._orders_ws is None:
            self._orders_ws = ensure_worksheet(self.spreadsheet, self.settings.google_sheet_tab)
        return self._orders_ws

    def _get_user_settings_ws(self) -> gspread.Worksheet:
        if self._user_settings_ws is None:
            ws = ensure_worksheet(self.spreadsheet, USER_SETTINGS_TAB)
            if ws.row_values(1) != USER_SETTINGS_HEADERS:
                ws.update("A1:E1", [USER_SETTINGS_HEADERS])
            self._user_settings_ws = ws
        return self._user_settings_ws

    def setup(self) -> None:
        setup_sheet(self.settings)

    def append_order(self, order: dict[str, str]) -> dict[str, str]:
        ws = self._get_orders_ws()
        now = _now(self.settings)
        order_id = f"C-{len(ws.get_all_records()) + 1:04d}"
        row = {
            "ID": order_id,
            "Date": now.strftime("%Y-%m-%d"),
            "Customer Name": order.get("Customer Name", "").strip(),
            "Phone": order.get("Phone", "").strip(),
            "Item": order.get("Item", "").strip(),
            "Size": order.get("Size", "").strip(),
            "Color": order.get("Color", "").strip(),
            "Quantity": str(order.get("Quantity", "")).strip(),
            "Amount": str(_parse_amount(order.get("Amount", "0"))),
            "Payment Status": order.get("Payment Status", "").strip(),
            "Payment Method": order.get("Payment Method", "").strip(),
            "Delivery Status": order.get("Delivery Status", "").strip(),
            "Address/Note": order.get("Address/Note", "").strip(),
            "Status": order.get("Status", "Open").strip() or "Open",
            "Created At": now.isoformat(timespec="seconds"),
            "Updated At": now.isoformat(timespec="seconds"),
        }
        ws.append_row([row[h] for h in HEADERS], value_input_option="USER_ENTERED")
        return row

    def unpaid_orders(self) -> list[dict[str, str]]:
        ws = self._get_orders_ws()
        return [
            {str(k): str(v) for k, v in row.items()}
            for row in ws.get_all_records()
            if row.get("Status", "Open") == "Open"
            and row.get("Payment Status") in UNPAID_PAYMENT_STATUSES
        ]

    def pending_delivery_orders(self) -> list[dict[str, str]]:
        ws = self._get_orders_ws()
        return [
            {str(k): str(v) for k, v in row.items()}
            for row in ws.get_all_records()
            if row.get("Status", "Open") == "Open"
            and row.get("Delivery Status") == PENDING_DELIVERY_STATUS
        ]

    def today_report(self) -> dict[str, int]:
        today = _now(self.settings).strftime("%Y-%m-%d")
        ws = self._get_orders_ws()
        orders = [
            row for row in ws.get_all_records()
            if row.get("Date") == today
        ]
        total_amount = sum(_parse_amount(row.get("Amount")) for row in orders)
        unpaid = [row for row in orders if row.get("Payment Status") in UNPAID_PAYMENT_STATUSES]
        pending = [row for row in orders if row.get("Delivery Status") == PENDING_DELIVERY_STATUS]
        return {
            "total_orders": len(orders),
            "total_amount": total_amount,
            "unpaid_amount": sum(_parse_amount(row.get("Amount")) for row in unpaid),
            "unpaid_count": len(unpaid),
            "pending_count": len(pending),
        }

    def get_user_language(self, telegram_user_id: int) -> str | None:
        ws = self._get_user_settings_ws()
        user_id = str(telegram_user_id)
        for row in ws.get_all_records():
            if str(row.get("Telegram User ID", "")) == user_id:
                lang = str(row.get("Language", "")).strip()
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
        ws = self._get_user_settings_ws()
        user_id = str(telegram_user_id)
        now = _now(self.settings).isoformat(timespec="seconds")
        values = ws.get_all_values()
        for index, row in enumerate(values[1:], start=2):
            if row and row[0] == user_id:
                ws.update(f"A{index}:E{index}", [[user_id, username or "", first_name or "", language, now]])
                return
        ws.append_row([user_id, username or "", first_name or "", language, now], value_input_option="USER_ENTERED")
