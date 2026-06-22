class FakeStorage:
    def unpaid_orders(self):
        return [{"ID": "C-0001"}]

    def pending_delivery_orders(self):
        return [{"ID": "C-0002"}]

    def today_report(self):
        return {
            "total_orders": 2,
            "total_amount": 48000,
            "unpaid_amount": 45000,
            "unpaid_count": 1,
            "pending_count": 1,
        }


def test_today_report_delegates_to_storage():
    from src.services.admin import AdminService

    service = AdminService(FakeStorage())

    report = service.today_report()

    assert report["total_orders"] == 2
    assert report["pending_count"] == 1


def test_unpaid_list_delegates_to_storage():
    from src.services.admin import AdminService

    service = AdminService(FakeStorage())

    rows = service.unpaid_orders()

    assert rows == [{"ID": "C-0001"}]


def test_pending_list_delegates_to_storage():
    from src.services.admin import AdminService

    service = AdminService(FakeStorage())

    rows = service.pending_delivery_orders()

    assert rows == [{"ID": "C-0002"}]
