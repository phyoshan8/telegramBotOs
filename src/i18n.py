from __future__ import annotations

import re
from telegram import ReplyKeyboardMarkup

TEXT = {
    "en": {
        "choose_language": "Please choose language / ဘာသာစကားရွေးပါ",
        "language_saved": "Language saved ✅",
        "welcome": "Hello 👋\nClothing Order Bot is ready.",
        "add_order": "➕ Add Order",
        "unpaid_list": "📋 Unpaid List",
        "pending_list": "🚚 Pending Delivery",
        "today_report": "📊 Today Report",
        "admin_panel": "🛠️ Admin Panel",
        "settings": "⚙️ Settings",
        "language": "🌐 Language",
        "back": "⬅️ Back",
        "confirm": "✅ Confirm",
        "change": "✏️ Change",
        "cancel": "❌ Cancel",
        "ask_name": "Customer name?",
        "ask_phone": "Phone number?",
        "ask_item": "Item? Example: Dress, T-shirt",
        "ask_size": "Size? Example: S, M, L, XL, Free Size",
        "ask_color": "Color?",
        "ask_quantity": "Quantity? Example: 1 or 2",
        "ask_amount": "Amount? Example: 45000",
        "ask_payment_status": "Choose payment status.",
        "ask_payment_method": "Choose payment method.",
        "ask_delivery_status": "Choose delivery status.",
        "ask_note": "Address/Note? Type '-' if none.",
        "invalid_quantity": "Quantity must be a number. Example: 2",
        "invalid_amount": "Amount must be a number. Example: 45000",
        "correct_question": "Is this correct?",
        "invalid_key": "Invalid key ❌\nPlease enter one of: Cus, Ph, Item, Size, Color, Qty, Amt, Pay, Method, Del, Note",
        "enter_new_value": "Enter new value for {field}.",
        "cancelled": "Cancelled. Back to main menu.",
        "settings_title": "Settings: choose what to change.",
        "admin_panel_title": "Admin panel: more actions will be added here.",
        "admin_access_denied": "Admin only ❌",
    },
    "my": {
        "choose_language": "ဘာသာစကားရွေးပါ။",
        "language_saved": "ဘာသာစကား သိမ်းပြီးပါပြီ ✅",
        "welcome": "မင်္ဂလာပါ 👋\nClothing Order Bot အသင့်ဖြစ်ပါပြီ။",
        "add_order": "➕ အော်ဒါထည့်ရန်",
        "unpaid_list": "📋 မရှင်းရစာရင်း",
        "pending_list": "🚚 ပို့ရန်စာရင်း",
        "today_report": "📊 ဒီနေ့ Report",
        "admin_panel": "🛠️ Admin Panel",
        "settings": "⚙️ Settings / ဘာသာစကား",
        "language": "🌐 ဘာသာစကား",
        "back": "⬅️ နောက်သို့",
        "confirm": "✅ အတည်ပြု",
        "change": "✏️ ပြင်မယ်",
        "cancel": "❌ မလုပ်တော့ပါ",
        "ask_name": "Customer နာမည် ရိုက်ပါ။",
        "ask_phone": "ဖုန်းနံပါတ် ရိုက်ပါ။",
        "ask_item": "ပစ္စည်းအမည် ရိုက်ပါ။ ဥပမာ Dress, T-shirt",
        "ask_size": "အရွယ်အစား ရိုက်ပါ။ ဥပမာ S, M, L, XL, Free Size",
        "ask_color": "အရောင် ရိုက်ပါ။",
        "ask_quantity": "အရေအတွက် ရိုက်ပါ။ ဥပမာ 1 သို့မဟုတ် 2",
        "ask_amount": "ငွေပမာဏ ရိုက်ပါ။ ဥပမာ 45000",
        "ask_payment_status": "Payment Status ရွေးပါ။",
        "ask_payment_method": "Payment Method ရွေးပါ။",
        "ask_delivery_status": "Delivery Status ရွေးပါ။",
        "ask_note": "Address/Note ရိုက်ပါ။ မရှိရင် '-' လို့ရိုက်ပါ။",
        "invalid_quantity": "အရေအတွက်ကို number နဲ့ပဲ ရိုက်ပါ။ ဥပမာ 2",
        "invalid_amount": "ငွေပမာဏကို number နဲ့ပဲ ရိုက်ပါ။ ဥပမာ 45000",
        "correct_question": "အချက်အလက်မှန်ပါသလား?",
        "invalid_key": "Short key မှားနေပါတယ် ❌\nCus, Ph, Item, Size, Color, Qty, Amt, Pay, Method, Del, Note ထဲက တစ်ခု ရိုက်ပါ။",
        "enter_new_value": "{field} အတွက် value အသစ် ရိုက်ပါ။",
        "cancelled": "မလုပ်တော့ပါ။ Main menu ပြန်သွားပါမယ်။",
        "settings_title": "Settings: ပြင်ချင်တာကို ရွေးပါ။",
        "admin_panel_title": "Admin panel: နောက်ထပ် action တွေ ဒီမှာ ထည့်သွားပါမယ်။",
        "admin_access_denied": "Admin only ❌",
    },
}

BUTTONS = {
    "add_order": {"➕ Add Order", "➕ အော်ဒါထည့်ရန်", "➕ Add Order / အော်ဒါထည့်ရန်"},
    "unpaid_list": {"📋 Unpaid List", "📋 မရှင်းရစာရင်း", "📋 Unpaid List / မရှင်းရစာရင်း"},
    "pending_list": {"🚚 Pending Delivery", "🚚 ပို့ရန်စာရင်း", "🚚 Pending / ပို့ရန်စာရင်း"},
    "today_report": {"📊 Today Report", "📊 ဒီနေ့ Report", "📊 Today Report / ဒီနေ့ Report"},
    "admin_panel": {"🛠️ Admin Panel"},
    "settings": {"⚙️ Settings", "⚙️ Settings / ဘာသာစကား"},
    "language": {"🌐 Language", "🌐 ဘာသာစကား"},
    "back": {"⬅️ Back", "⬅️ နောက်သို့"},
    "confirm": {"✅ Confirm", "✅ အတည်ပြု"},
    "change": {"✏️ Change", "✏️ ပြင်မယ်"},
    "cancel": {"❌ Cancel", "❌ မလုပ်တော့ပါ", "Cancel / မလုပ်တော့ပါ"},
}


def t(lang: str | None, key: str, **kwargs) -> str:
    lang = lang if lang in TEXT else "en"
    value = TEXT[lang].get(key, TEXT["en"].get(key, key))
    return value.format(**kwargs)


def button_regex(name: str) -> str:
    return "^(" + "|".join(re.escape(x) for x in BUTTONS[name]) + ")$"


def main_menu(lang: str, *, is_admin: bool = False) -> ReplyKeyboardMarkup:
    rows = [
        [t(lang, "add_order")],
        [t(lang, "unpaid_list"), t(lang, "pending_list")],
        [t(lang, "today_report"), t(lang, "settings")],
    ]
    if is_admin:
        rows.insert(2, [t(lang, "admin_panel")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def language_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["English", "မြန်မာ"]], resize_keyboard=True, one_time_keyboard=True)


def settings_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[t(lang, "language")], [t(lang, "back")]], resize_keyboard=True)


def confirm_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[t(lang, "confirm"), t(lang, "change")], [t(lang, "cancel")]], resize_keyboard=True)
