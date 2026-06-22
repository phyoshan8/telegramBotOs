from __future__ import annotations

import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from .config import load_settings
from .i18n import button_regex, confirm_menu, language_menu, main_menu, settings_menu, t
from .reports import EDIT_FIELDS, edit_key_help, list_message, normalize_edit_key, order_preview, saved_message, today_report_message
from .services import AdminService, OrderService
from .storage_factory import build_storage

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

(
    ASK_NAME,
    ASK_PHONE,
    ASK_ITEM,
    ASK_SIZE,
    ASK_COLOR,
    ASK_QUANTITY,
    ASK_AMOUNT,
    ASK_PAYMENT_STATUS,
    ASK_PAYMENT_METHOD,
    ASK_DELIVERY_STATUS,
    ASK_NOTE,
    ASK_CONFIRM,
    ASK_EDIT_KEY,
    ASK_EDIT_VALUE,
) = range(14)

PAYMENT_STATUS_MENU = ReplyKeyboardMarkup([["Paid", "Unpaid"], ["COD", "Deposit"]], resize_keyboard=True, one_time_keyboard=True)
PAYMENT_METHOD_MENU = ReplyKeyboardMarkup([["KPay", "Wave"], ["AYA Pay", "CB Pay"], ["Cash", "Other"]], resize_keyboard=True, one_time_keyboard=True)
DELIVERY_STATUS_MENU = ReplyKeyboardMarkup([["Pending", "Delivered"], ["Pickup", "Cancelled"], ["Returned"]], resize_keyboard=True, one_time_keyboard=True)


def settings_from_context(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["settings"]


def storage_from_context(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["storage"]


def order_service_from_context(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["order_service"]


def admin_service_from_context(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["admin_service"]


def get_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    if "lang" in context.user_data:
        return context.user_data["lang"]
    user = update.effective_user
    if not user:
        return None
    lang = storage_from_context(context).get_user_language(user.id)
    if lang:
        context.user_data["lang"] = lang
    return lang


def user_identity(update: Update) -> tuple[int, str | None, str | None]:
    user = update.effective_user
    return user.id, user.username, user.first_name


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_lang(update, context)
    if not lang:
        await update.message.reply_text(t("en", "choose_language"), reply_markup=language_menu())
        return
    await update.message.reply_text(t(lang, "welcome"), reply_markup=main_menu(lang))


async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    lang = "my" if text == "မြန်မာ" else "en"
    user_id, username, first_name = user_identity(update)
    storage_from_context(context).set_user_language(user_id, username, first_name, lang)
    context.user_data["lang"] = lang
    await update.message.reply_text(t(lang, "language_saved"), reply_markup=main_menu(lang))


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_lang(update, context) or "en"
    await update.message.reply_text(t(lang, "settings_title"), reply_markup=settings_menu(lang))


async def ask_language_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(t(get_lang(update, context) or "en", "choose_language"), reply_markup=language_menu())


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_lang(update, context) or "en"
    await update.message.reply_text(t(lang, "welcome"), reply_markup=main_menu(lang))


async def begin_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(update, context)
    if not lang:
        await update.message.reply_text(t("en", "choose_language"), reply_markup=language_menu())
        return ConversationHandler.END
    context.user_data["order"] = {}
    await update.message.reply_text(t(lang, "ask_name"), reply_markup=ReplyKeyboardRemove())
    return ASK_NAME


async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["order"]["Customer Name"] = update.message.text.strip()
    await update.message.reply_text(t(get_lang(update, context), "ask_phone"))
    return ASK_PHONE


async def ask_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["order"]["Phone"] = update.message.text.strip()
    await update.message.reply_text(t(get_lang(update, context), "ask_item"))
    return ASK_ITEM


async def ask_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["order"]["Item"] = update.message.text.strip()
    await update.message.reply_text(t(get_lang(update, context), "ask_size"))
    return ASK_SIZE


async def ask_color(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["order"]["Size"] = update.message.text.strip()
    await update.message.reply_text(t(get_lang(update, context), "ask_color"))
    return ASK_COLOR


async def ask_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["order"]["Color"] = update.message.text.strip()
    await update.message.reply_text(t(get_lang(update, context), "ask_quantity"))
    return ASK_QUANTITY


async def ask_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(update, context)
    qty = update.message.text.strip().replace(",", "")
    if not qty.isdigit():
        await update.message.reply_text(t(lang, "invalid_quantity"))
        return ASK_QUANTITY
    context.user_data["order"]["Quantity"] = qty
    await update.message.reply_text(t(lang, "ask_amount"))
    return ASK_AMOUNT


async def ask_payment_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(update, context)
    amount = update.message.text.strip().replace(",", "")
    if not amount.isdigit():
        await update.message.reply_text(t(lang, "invalid_amount"))
        return ASK_AMOUNT
    context.user_data["order"]["Amount"] = amount
    await update.message.reply_text(t(lang, "ask_payment_status"), reply_markup=PAYMENT_STATUS_MENU)
    return ASK_PAYMENT_STATUS


async def ask_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["order"]["Payment Status"] = update.message.text.strip()
    await update.message.reply_text(t(get_lang(update, context), "ask_payment_method"), reply_markup=PAYMENT_METHOD_MENU)
    return ASK_PAYMENT_METHOD


async def ask_delivery_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["order"]["Payment Method"] = update.message.text.strip()
    await update.message.reply_text(t(get_lang(update, context), "ask_delivery_status"), reply_markup=DELIVERY_STATUS_MENU)
    return ASK_DELIVERY_STATUS


async def ask_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["order"]["Delivery Status"] = update.message.text.strip()
    await update.message.reply_text(t(get_lang(update, context), "ask_note"), reply_markup=ReplyKeyboardRemove())
    return ASK_NOTE


async def show_preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(update, context) or "en"
    context.user_data["order"]["Address/Note"] = update.message.text.strip()
    await update.message.reply_text(
        order_preview(context.user_data["order"], lang) + "\n\n" + t(lang, "correct_question"),
        reply_markup=confirm_menu(lang),
    )
    return ASK_CONFIRM


async def confirm_or_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(update, context) or "en"
    text = update.message.text.strip()
    if text in {"✅ Confirm", "✅ အတည်ပြု"}:
        context.user_data["order"]["Status"] = "Open"
        row = order_service_from_context(context).create_order(context.user_data["order"])
        context.user_data.pop("order", None)
        context.user_data.pop("edit_key", None)
        await update.message.reply_text(saved_message(row, lang), reply_markup=main_menu(lang))
        return ConversationHandler.END
    if text in {"✏️ Change", "✏️ ပြင်မယ်"}:
        await update.message.reply_text(edit_key_help(lang), reply_markup=ReplyKeyboardRemove())
        return ASK_EDIT_KEY
    if text in {"❌ Cancel", "❌ မလုပ်တော့ပါ", "Cancel / မလုပ်တော့ပါ"}:
        return await cancel(update, context)
    await update.message.reply_text(t(lang, "correct_question"), reply_markup=confirm_menu(lang))
    return ASK_CONFIRM


async def receive_edit_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(update, context) or "en"
    key = normalize_edit_key(update.message.text)
    if not key:
        await update.message.reply_text(t(lang, "invalid_key"))
        return ASK_EDIT_KEY
    context.user_data["edit_key"] = key
    if key == "Pay":
        await update.message.reply_text(t(lang, "ask_payment_status"), reply_markup=PAYMENT_STATUS_MENU)
    elif key == "Method":
        await update.message.reply_text(t(lang, "ask_payment_method"), reply_markup=PAYMENT_METHOD_MENU)
    elif key == "Del":
        await update.message.reply_text(t(lang, "ask_delivery_status"), reply_markup=DELIVERY_STATUS_MENU)
    else:
        await update.message.reply_text(t(lang, "enter_new_value", field=EDIT_FIELDS[key]), reply_markup=ReplyKeyboardRemove())
    return ASK_EDIT_VALUE


async def receive_edit_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(update, context) or "en"
    key = context.user_data.get("edit_key")
    field = EDIT_FIELDS[key]
    value = update.message.text.strip()
    cleaned = value.replace(",", "")
    if key == "Qty" and not cleaned.isdigit():
        await update.message.reply_text(t(lang, "invalid_quantity"))
        return ASK_EDIT_VALUE
    if key == "Amt" and not cleaned.isdigit():
        await update.message.reply_text(t(lang, "invalid_amount"))
        return ASK_EDIT_VALUE
    context.user_data["order"][field] = cleaned if key in {"Qty", "Amt"} else value
    context.user_data.pop("edit_key", None)
    await update.message.reply_text(
        order_preview(context.user_data["order"], lang) + "\n\n" + t(lang, "correct_question"),
        reply_markup=confirm_menu(lang),
    )
    return ASK_CONFIRM


async def show_unpaid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_lang(update, context) or "en"
    rows = admin_service_from_context(context).unpaid_orders()
    title = "Unpaid List 📋" if lang == "en" else "မရှင်းရစာရင်း 📋"
    empty = "No unpaid/COD/deposit orders ✅" if lang == "en" else "မရှင်းရ/COD/Deposit order မရှိပါ ✅"
    await update.message.reply_text(list_message(title, rows, empty), reply_markup=main_menu(lang))


async def show_pending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_lang(update, context) or "en"
    rows = admin_service_from_context(context).pending_delivery_orders()
    title = "Pending Delivery 🚚" if lang == "en" else "ပို့ရန်စာရင်း 🚚"
    empty = "No pending delivery orders ✅" if lang == "en" else "ပို့ရန်ကျန် order မရှိပါ ✅"
    await update.message.reply_text(list_message(title, rows, empty), reply_markup=main_menu(lang))


async def show_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_lang(update, context) or "en"
    report = admin_service_from_context(context).today_report()
    await update.message.reply_text(today_report_message(report, lang), reply_markup=main_menu(lang))


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(update, context) or "en"
    context.user_data.pop("order", None)
    context.user_data.pop("edit_key", None)
    await update.message.reply_text(t(lang, "cancelled"), reply_markup=main_menu(lang))
    return ConversationHandler.END


def main() -> None:
    settings = load_settings()
    storage = build_storage(settings)
    storage.setup()

    app = Application.builder().token(settings.telegram_bot_token).build()
    app.bot_data["settings"] = settings
    app.bot_data["storage"] = storage
    app.bot_data["order_service"] = OrderService(storage)
    app.bot_data["admin_service"] = AdminService(storage)

    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(button_regex("add_order")), begin_order)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_item)],
            ASK_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_size)],
            ASK_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_color)],
            ASK_COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_quantity)],
            ASK_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_amount)],
            ASK_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_payment_status)],
            ASK_PAYMENT_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_payment_method)],
            ASK_PAYMENT_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_delivery_status)],
            ASK_DELIVERY_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_note)],
            ASK_NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, show_preview)],
            ASK_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_or_change)],
            ASK_EDIT_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_edit_key)],
            ASK_EDIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_edit_value)],
        },
        fallbacks=[CommandHandler("cancel", cancel), MessageHandler(filters.Regex(button_regex("cancel")), cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^(English|မြန်မာ)$"), choose_language))
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.Regex(button_regex("settings")), show_settings))
    app.add_handler(MessageHandler(filters.Regex(button_regex("language")), ask_language_change))
    app.add_handler(MessageHandler(filters.Regex(button_regex("back")), back_to_menu))
    app.add_handler(MessageHandler(filters.Regex(button_regex("unpaid_list")), show_unpaid))
    app.add_handler(MessageHandler(filters.Regex(button_regex("pending_list")), show_pending))
    app.add_handler(MessageHandler(filters.Regex(button_regex("today_report")), show_report))

    logger.info("Bot started. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
