from src.storage_mirror import MirroredStorage


class FakePrimary:
    def __init__(self):
        self.setup_called = False
        self.append_calls = []
        self.language_calls = []

    def setup(self):
        self.setup_called = True

    def append_order(self, order):
        self.append_calls.append(order)
        return {"ID": "C-0001", **order}

    def unpaid_orders(self):
        return [{"ID": "C-0001"}]

    def pending_delivery_orders(self):
        return [{"ID": "C-0002"}]

    def today_report(self):
        return {
            "total_orders": 1,
            "total_amount": 1000,
            "unpaid_amount": 1000,
            "unpaid_count": 1,
            "pending_count": 0,
        }

    def get_user_language(self, telegram_user_id):
        return "en"

    def get_user_role(self, telegram_user_id):
        return "admin"

    def set_user_language(self, telegram_user_id, username, first_name, language):
        self.language_calls.append((telegram_user_id, username, first_name, language))


class FakeMirror:
    def __init__(self):
        self.setup_called = False
        self.rows = []

    def setup(self):
        self.setup_called = True

    def export_order(self, row):
        self.rows.append(row)


def test_mirrored_storage_appends_to_primary_then_exports_saved_row():
    primary = FakePrimary()
    mirror = FakeMirror()
    storage = MirroredStorage(primary=primary, mirror=mirror)

    saved = storage.append_order({"Customer Name": "Aye"})

    assert saved["ID"] == "C-0001"
    assert primary.append_calls == [{"Customer Name": "Aye"}]
    assert mirror.rows == [saved]


def test_mirrored_storage_delegates_reads_and_language_to_primary():
    primary = FakePrimary()
    mirror = FakeMirror()
    storage = MirroredStorage(primary=primary, mirror=mirror)

    storage.setup()
    storage.set_user_language(10, "aye", "Aye", "my")

    assert storage.unpaid_orders() == [{"ID": "C-0001"}]
    assert storage.pending_delivery_orders() == [{"ID": "C-0002"}]
    assert storage.today_report()["total_orders"] == 1
    assert storage.get_user_language(10) == "en"
    assert storage.get_user_role(10) == "admin"
    assert primary.setup_called is True
    assert mirror.setup_called is True
    assert primary.language_calls == [(10, "aye", "Aye", "my")]
