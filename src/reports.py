from __future__ import annotations


def money(value: object) -> str:
    try:
        amount = int(float(str(value).replace(",", "") or 0))
    except ValueError:
        amount = 0
    return f"{amount:,} MMK"


EDIT_FIELDS = {
    "Cus": "Customer Name",
    "Ph": "Phone",
    "Item": "Item",
    "Size": "Size",
    "Color": "Color",
    "Qty": "Quantity",
    "Amt": "Amount",
    "Pay": "Payment Status",
    "Method": "Payment Method",
    "Del": "Delivery Status",
    "Note": "Address/Note",
}

KEY_ALIASES = {key.lower(): key for key in EDIT_FIELDS}


def normalize_edit_key(text: str) -> str | None:
    """Return canonical edit key or None.

    Logic: clients may type `qty`, `QTY`, or ` Qty `. We accept those.
    But we do not guess long/wrong words like `Quantity`, because guessing can
    edit the wrong field. Wrong short keys must produce a clear error.
    """
    return KEY_ALIASES.get(text.strip().lower())


def edit_key_help(lang: str = "en") -> str:
    title = "Which field do you want to change? Enter short key:" if lang == "en" else "ဘယ် field ကို ပြင်ချင်ပါသလဲ? Short key ရိုက်ပါ:"
    return "\n".join(
        [
            title,
            "",
            "Cus = Customer Name",
            "Ph = Phone",
            "Item = Item",
            "Size = Size",
            "Color = Color",
            "Qty = Quantity",
            "Amt = Amount",
            "Pay = Payment Status",
            "Method = Payment Method",
            "Del = Delivery Status",
            "Note = Address/Note",
        ]
    )


def order_preview(order: dict[str, str], lang: str = "en") -> str:
    title = "Order Preview" if lang == "en" else "အော်ဒါ စစ်ဆေးရန်"
    lines = [
        title,
        "",
        f"Cus: {order.get('Customer Name', '-')}",
        f"Ph: {order.get('Phone', '-')}",
        f"Item: {order.get('Item', '-')}",
        f"Size: {order.get('Size', '-')}",
        f"Color: {order.get('Color', '-')}",
        f"Qty: {order.get('Quantity', '-')}",
        f"Amt: {money(order.get('Amount', '0'))}",
        f"Pay: {order.get('Payment Status', '-')}",
        f"Method: {order.get('Payment Method', '-')}",
        f"Del: {order.get('Delivery Status', '-')}",
        f"Note: {order.get('Address/Note', '-')}",
    ]
    return "\n".join(lines)


def order_line(row: dict[str, str], idx: int | None = None) -> str:
    prefix = f"{idx}. " if idx is not None else ""
    item = " ".join(x for x in [row.get("Item"), row.get("Size"), row.get("Color")] if x)
    qty = row.get("Quantity") or "-"
    return (
        f"{prefix}{row.get('Customer Name','-')} - {item or '-'} - Qty {qty} - "
        f"{money(row.get('Amount', '0'))} - {row.get('Phone','-')}\n"
        f"   Pay: {row.get('Payment Status','-')} / {row.get('Payment Method','-')} | "
        f"Delivery: {row.get('Delivery Status','-')}"
    )


def saved_message(row: dict[str, str], lang: str = "en") -> str:
    prefix = "Saved ✅" if lang == "en" else "သိမ်းပြီးပါပြီ ✅"
    return (
        f"{prefix}\n"
        f"Order ID: {row.get('ID')}\n"
        f"Customer: {row.get('Customer Name')}\n"
        f"Item: {row.get('Item')} / {row.get('Size')} / {row.get('Color')}\n"
        f"Qty: {row.get('Quantity')}\n"
        f"Amount: {money(row.get('Amount'))}\n"
        f"Payment: {row.get('Payment Status')} / {row.get('Payment Method')}\n"
        f"Delivery: {row.get('Delivery Status')}"
    )


def list_message(title: str, rows: list[dict[str, str]], empty_text: str) -> str:
    if not rows:
        return empty_text
    lines = [title, ""]
    for idx, row in enumerate(rows[:20], start=1):
        lines.append(order_line(row, idx))
    if len(rows) > 20:
        lines.append(f"\nနောက်ထပ် {len(rows) - 20} ခု ရှိသေးပါတယ်။")
    return "\n".join(lines)


def today_report_message(report: dict[str, int], lang: str = "en") -> str:
    if lang == "my":
        return (
            "ဒီနေ့ Report 📊\n\n"
            f"Order အရေအတွက်: {report['total_orders']}\n"
            f"စုစုပေါင်းငွေ: {money(report['total_amount'])}\n"
            f"မရှင်းရ/COD/Deposit: {money(report['unpaid_amount'])}\n"
            f"မရှင်းရ Order: {report['unpaid_count']}\n"
            f"ပို့ရန်ကျန်: {report['pending_count']}"
        )
    return (
        "Today Report 📊\n\n"
        f"Total orders: {report['total_orders']}\n"
        f"Total amount: {money(report['total_amount'])}\n"
        f"Unpaid/COD/Deposit: {money(report['unpaid_amount'])}\n"
        f"Unpaid orders: {report['unpaid_count']}\n"
        f"Pending delivery: {report['pending_count']}"
    )
