class FakeStorage:
    def __init__(self):
        self.saved_order = None

    def append_order(self, order):
        self.saved_order = order
        return {"ID": "C-0001", **order}


def test_create_order_normalizes_numeric_fields():
    from src.services.orders import OrderService

    storage = FakeStorage()
    service = OrderService(storage)

    row = service.create_order(
        {
            "Customer Name": "May Thu",
            "Quantity": "1,200",
            "Amount": "45,000",
        }
    )

    assert storage.saved_order["Quantity"] == "1200"
    assert storage.saved_order["Amount"] == "45000"
    assert row["ID"] == "C-0001"


def test_prepare_order_defaults_status_to_open():
    from src.services.orders import OrderService

    storage = FakeStorage()
    service = OrderService(storage)

    prepared = service.prepare_order({"Customer Name": "May Thu", "Quantity": "2", "Amount": "3000"})

    assert prepared["Status"] == "Open"
