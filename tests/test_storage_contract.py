from src.storage_sheets import GoogleSheetsStorage


class FakeStorage:
    def setup(self):
        return None

    def append_order(self, order):
        return order

    def unpaid_orders(self):
        return []

    def pending_delivery_orders(self):
        return []

    def today_report(self):
        return {
            "total_orders": 0,
            "total_amount": 0,
            "unpaid_amount": 0,
            "unpaid_count": 0,
            "pending_count": 0,
        }

    def get_user_language(self, telegram_user_id):
        return None

    def set_user_language(self, telegram_user_id, username, first_name, language):
        return None


REQUIRED_METHODS = [
    "setup",
    "append_order",
    "unpaid_orders",
    "pending_delivery_orders",
    "today_report",
    "get_user_language",
    "set_user_language",
]


def test_fake_storage_shape_matches_expected_contract():
    storage = FakeStorage()
    for method_name in REQUIRED_METHODS:
        assert hasattr(storage, method_name)


def test_google_sheets_storage_exposes_required_methods():
    for method_name in REQUIRED_METHODS:
        assert hasattr(GoogleSheetsStorage, method_name)
