class FakeStorage:
    def __init__(self, role: str = "seller") -> None:
        self.role = role

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

    def get_user_role(self, telegram_user_id: int) -> str:
        return self.role


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


def test_is_admin_user_true_for_admin_role():
    from src.services.admin import AdminService

    service = AdminService(FakeStorage(role="admin"))

    assert service.is_admin_user(123) is True


def test_is_admin_user_false_for_seller_role():
    from src.services.admin import AdminService

    service = AdminService(FakeStorage(role="seller"))

    assert service.is_admin_user(123) is False


def test_is_admin_user_false_when_storage_has_no_role_method():
    from src.services.admin import AdminService

    class NoRoleStorage:
        def today_report(self):
            return {}

        def unpaid_orders(self):
            return []

        def pending_delivery_orders(self):
            return []

    service = AdminService(NoRoleStorage())

    assert service.is_admin_user(123) is False


def test_is_admin_user_false_for_blank_role():
    from src.services.admin import AdminService

    service = AdminService(FakeStorage(role=""))

    assert service.is_admin_user(123) is False


def test_is_admin_user_true_for_role_with_spaces_and_caps():
    from src.services.admin import AdminService

    service = AdminService(FakeStorage(role=" Admin "))

    assert service.is_admin_user(123) is True
