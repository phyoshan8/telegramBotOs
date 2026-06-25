from src.i18n import main_menu, t


def test_admin_menu_contains_report_and_admin_actions():
    markup = main_menu("en", is_admin=True)
    keyboard = [[button.text for button in row] for row in markup.keyboard]

    assert [t("en", "admin_panel")] in keyboard
    assert [t("en", "today_report"), t("en", "settings")] in keyboard


def test_non_admin_users_do_not_see_admin_actions():
    markup = main_menu("en", is_admin=False)
    keyboard = [[button.text for button in row] for row in markup.keyboard]

    assert [t("en", "admin_panel")] not in keyboard