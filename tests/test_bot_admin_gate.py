from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from src.bot import main_menu_for, show_admin_panel
from src.i18n import t


def keyboard_text(markup):
    return [[button.text for button in row] for row in markup.keyboard]


class FakeStorage:
    def get_user_language(self, telegram_user_id):
        return "en"


class FakeAdminService:
    def __init__(self, is_admin: bool):
        self.is_admin = is_admin

    def is_admin_user(self, telegram_user_id):
        return self.is_admin


def make_context(*, is_admin: bool):
    return SimpleNamespace(
        user_data={},
        application=SimpleNamespace(
            bot_data={
                "storage": FakeStorage(),
                "admin_service": FakeAdminService(is_admin=is_admin),
            }
        ),
    )


def make_update():
    return SimpleNamespace(
        effective_user=SimpleNamespace(id=123, username="aye", first_name="Aye"),
        message=SimpleNamespace(text="", reply_text=AsyncMock()),
    )


def test_main_menu_for_adds_admin_button_for_admin_user():
    update = make_update()
    context = make_context(is_admin=True)

    markup = main_menu_for(update, context, "en")

    assert [t("en", "admin_panel")] in keyboard_text(markup)


def test_main_menu_for_hides_admin_button_for_non_admin_user():
    update = make_update()
    context = make_context(is_admin=False)

    markup = main_menu_for(update, context, "en")

    assert [t("en", "admin_panel")] not in keyboard_text(markup)


def test_show_admin_panel_blocks_non_admin_user():
    update = make_update()
    context = make_context(is_admin=False)

    asyncio.run(show_admin_panel(update, context))

    update.message.reply_text.assert_awaited_once()
    args, kwargs = update.message.reply_text.await_args
    assert args[0] == t("en", "admin_access_denied")
    assert [t("en", "admin_panel")] not in keyboard_text(kwargs["reply_markup"])


def test_show_admin_panel_allows_admin_user():
    update = make_update()
    context = make_context(is_admin=True)

    asyncio.run(show_admin_panel(update, context))

    update.message.reply_text.assert_awaited_once()
    args, kwargs = update.message.reply_text.await_args
    assert args[0] == t("en", "admin_panel_title")
    assert [t("en", "admin_panel")] in keyboard_text(kwargs["reply_markup"])
