from src.reports import normalize_edit_key, order_preview


def test_normalize_edit_key_accepts_quantity_and_case_insensitive_keys():
    assert normalize_edit_key("cus") == "Cus"
    assert normalize_edit_key("CUS") == "Cus"
    assert normalize_edit_key(" Qty ") == "Qty"
    assert normalize_edit_key("amt") == "Amt"


def test_normalize_edit_key_rejects_unknown_keys():
    assert normalize_edit_key("Quantity") is None
    assert normalize_edit_key("Customer") is None
    assert normalize_edit_key("wrong") is None


def test_order_preview_includes_quantity_and_core_fields():
    preview = order_preview(
        {
            "Customer Name": "May Thu",
            "Phone": "09911112222",
            "Item": "Dress",
            "Size": "M",
            "Color": "Black",
            "Quantity": "2",
            "Amount": "45000",
            "Payment Status": "Unpaid",
            "Payment Method": "KPay",
            "Delivery Status": "Pending",
            "Address/Note": "Yangon",
        },
        "en",
    )
    assert "May Thu" in preview
    assert "Qty: 2" in preview
    assert "Dress" in preview
    assert "45,000 MMK" in preview
