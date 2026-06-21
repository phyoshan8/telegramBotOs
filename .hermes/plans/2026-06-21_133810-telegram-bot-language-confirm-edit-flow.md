# Telegram Bot Language, Confirm, and Edit Flow Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Update the Telegram clothing seller bot so each client first chooses Burmese or English, can later change language in Settings, and must confirm or edit an order before it is saved to Google Sheets.

**Architecture:** Add a lightweight settings layer backed by the existing Google Sheet `Settings` tab. Store each Telegram user’s language preference and use it to render bot prompts/buttons. Change the add-order flow so collected data is held in Telegram `context.user_data` first, then shown as a preview with `Confirm / အတည်ပြု` or `Change / ပြင်မယ်`; only confirmed orders are appended to the `Orders` tab. Add an edit-by-short-key loop with strict validation so wrong short keys return an error and ask again.

**Tech Stack:** Python 3.13, `python-telegram-bot`, `gspread`, Google Sheets, `.env`, existing project at `/home/phyoshan8/automation-projects/telegram-clothing-order-bot`.

---

## Current Context

Existing project path:

```text
/home/phyoshan8/automation-projects/telegram-clothing-order-bot
```

Existing important files:

```text
src/bot.py
src/config.py
src/storage_sheets.py
src/reports.py
src/sheet_setup.py
.env
```

Current behavior:

- Bot starts with `/start`.
- Bot shows mixed Burmese/English menu.
- Add Order flow asks fields one by one.
- After final Address/Note, bot saves directly to Google Sheets.
- Google Sheet backend works and has an `Orders` tab and `Settings` tab.

Requested new behavior:

1. First bot start should ask user to choose language:
   - Burmese
   - English
2. Language can later be changed from a Settings button/menu.
3. When order questions are completed, do not save directly.
4. Show order preview/status summary.
5. Offer:
   - Confirm / save
   - Change / edit wrong field
6. If Change is clicked, client chooses field by short key.
7. Short keys must be validated.
8. If wrong short key is entered, return an error message and ask again.
9. Only save after confirmation.

---

## Proposed UX

### First `/start`

If no language is stored for Telegram user:

```text
Please choose language / ဘာသာစကားရွေးပါ

[English]
[မြန်မာ]
```

If language already exists:

Show main menu in selected language.

### Main Menu English

```text
[➕ Add Order]
[📋 Unpaid List] [🚚 Pending Delivery]
[📊 Today Report]
[⚙️ Settings]
```

### Main Menu Burmese

```text
[➕ အော်ဒါထည့်ရန်]
[📋 မရှင်းရစာရင်း] [🚚 ပို့ရန်စာရင်း]
[📊 ဒီနေ့ Report]
[⚙️ Settings / ဘာသာစကား]
```

### Settings Menu

```text
Settings
Choose what to change:

[🌐 Language]
[⬅️ Back]
```

Language selection updates the `Settings` tab or a new `User Settings` tab.

### Add Order Flow

Fields:

1. Customer Name
2. Phone
3. Item
4. Size
5. Color
6. Amount
7. Payment Status
8. Payment Method
9. Delivery Status
10. Address/Note

After all fields are collected, show preview:

```text
Order Preview / အော်ဒါ စစ်ဆေးရန်

Cus: May Thu
Ph: 09911112222
Item: Dress
Size: M
Color: Black
Amt: 45,000 MMK
Pay: Unpaid
Method: KPay
Delivery: Pending
Note: Yangon

Correct?
```

Buttons:

```text
[✅ Confirm / အတည်ပြု]
[✏️ Change / ပြင်မယ်]
[❌ Cancel]
```

### Edit Flow

If Change clicked:

```text
Which field do you want to change?
Enter short key:

Cus = Customer Name
Ph = Phone
Item = Item
Size = Size
Color = Color
Amt = Amount
Pay = Payment Status
Method = Payment Method
Del = Delivery Status
Note = Address/Note
```

If user enters wrong key:

```text
Invalid key ❌
Please enter one of:
Cus, Ph, Item, Size, Color, Amt, Pay, Method, Del, Note
```

If valid key:

- Ask for new value.
- If `Pay`, show payment status buttons.
- If `Method`, show payment method buttons.
- If `Del`, show delivery status buttons.
- If `Amt`, validate number.
- Update draft order.
- Show preview again.

Only after `Confirm` is clicked:

- Append to Google Sheets.
- Show saved confirmation.

---

## Data Design

### Existing Orders headers

Keep existing order columns:

```text
ID
Date
Customer Name
Phone
Item
Size
Color
Amount
Payment Status
Payment Method
Delivery Status
Address/Note
Status
Created At
Updated At
```

### New User Settings tab

Create a new tab:

```text
User Settings
```

Headers:

```text
Telegram User ID
Username
First Name
Language
Updated At
```

Reason:

The existing `Settings` tab is shop/global settings. Language is per Telegram user/admin, so it should be stored separately.

For first version, if multiple admins use the same bot, each can choose their own language.

---

## Short Key Mapping

Use these exact edit keys:

```python
EDIT_FIELDS = {
    "Cus": "Customer Name",
    "Ph": "Phone",
    "Item": "Item",
    "Size": "Size",
    "Color": "Color",
    "Amt": "Amount",
    "Pay": "Payment Status",
    "Method": "Payment Method",
    "Del": "Delivery Status",
    "Note": "Address/Note",
}
```

Validation rule:

- Strip whitespace.
- Match case-insensitively but normalize to canonical key.
- If not found, return error and ask again.
- Do not proceed to value entry until key is valid.

---

## Step-by-Step Plan

### Task 1: Add language/settings storage helpers

**Objective:** Store and read each Telegram user’s selected language from Google Sheets.

**Files:**

- Modify: `/home/phyoshan8/automation-projects/telegram-clothing-order-bot/src/storage_sheets.py`
- Modify: `/home/phyoshan8/automation-projects/telegram-clothing-order-bot/src/sheet_setup.py` indirectly through `setup_sheet()`

**Step 1: Add constants**

In `src/storage_sheets.py`, add:

```python
USER_SETTINGS_TAB = "User Settings"
USER_SETTINGS_HEADERS = [
    "Telegram User ID",
    "Username",
    "First Name",
    "Language",
    "Updated At",
]
```

**Step 2: Update `setup_sheet()`**

Add `User Settings` tab to the created/verified tabs.

Pseudo-code:

```python
user_settings = ensure_worksheet(spreadsheet, USER_SETTINGS_TAB)
if user_settings.row_values(1) != USER_SETTINGS_HEADERS:
    user_settings.update("A1:E1", [USER_SETTINGS_HEADERS])
    user_settings.freeze(rows=1)
```

**Step 3: Add helper functions**

Add:

```python
def get_user_language(settings: Settings, telegram_user_id: int) -> str | None:
    ...

def set_user_language(
    settings: Settings,
    telegram_user_id: int,
    username: str | None,
    first_name: str | None,
    language: str,
) -> None:
    ...
```

Rules:

- Language values should be exactly `en` or `my`.
- `get_user_language()` returns `None` if no row exists.
- `set_user_language()` updates existing row if user ID exists; otherwise appends a new row.

**Step 4: Verify manually**

Run:

```bash
cd /home/phyoshan8/automation-projects/telegram-clothing-order-bot
. .venv/bin/activate
python -m src.sheet_setup
```

Expected:

- `User Settings` tab exists.
- Header row is created.

**Step 5: Commit**

```bash
git add src/storage_sheets.py src/sheet_setup.py
git commit -m "feat: add user language settings storage"
```

If this project is not yet a git repo, skip commit.

---

### Task 2: Add message/keyboard localization module

**Objective:** Centralize Burmese/English text so bot logic stays clean.

**Files:**

- Create: `/home/phyoshan8/automation-projects/telegram-clothing-order-bot/src/i18n.py`

**Step 1: Create text dictionaries**

Create `src/i18n.py`:

```python
from __future__ import annotations

TEXT = {
    "en": {
        "choose_language": "Please choose language.",
        "language_saved": "Language saved ✅",
        "welcome": "Hello 👋\nClothing Order Bot is ready.",
        "add_order": "➕ Add Order",
        "unpaid_list": "📋 Unpaid List",
        "pending_list": "🚚 Pending Delivery",
        "today_report": "📊 Today Report",
        "settings": "⚙️ Settings",
        "back": "⬅️ Back",
        "confirm": "✅ Confirm",
        "change": "✏️ Change",
        "cancel": "❌ Cancel",
        "ask_name": "Customer name?",
        "ask_phone": "Phone number?",
        "ask_item": "Item? Example: Dress, T-shirt",
        "ask_size": "Size? Example: S, M, L, XL, Free Size",
        "ask_color": "Color?",
        "ask_amount": "Amount? Example: 45000",
        "ask_payment_status": "Choose payment status.",
        "ask_payment_method": "Choose payment method.",
        "ask_delivery_status": "Choose delivery status.",
        "ask_note": "Address/Note? Type '-' if none.",
        "invalid_amount": "Amount must be a number. Example: 45000",
        "preview_title": "Order Preview",
        "correct_question": "Is this correct?",
        "which_field": "Which field do you want to change? Enter short key:",
        "invalid_key": "Invalid key ❌\nPlease enter one of: Cus, Ph, Item, Size, Color, Amt, Pay, Method, Del, Note",
        "enter_new_value": "Enter new value for {field}.",
        "saved": "Saved ✅",
        "cancelled": "Cancelled. Back to main menu.",
    },
    "my": {
        "choose_language": "ဘာသာစကားရွေးပါ။",
        "language_saved": "ဘာသာစကား သိမ်းပြီးပါပြီ ✅",
        "welcome": "မင်္ဂလာပါ 👋\nClothing Order Bot အသင့်ဖြစ်ပါပြီ။",
        "add_order": "➕ အော်ဒါထည့်ရန်",
        "unpaid_list": "📋 မရှင်းရစာရင်း",
        "pending_list": "🚚 ပို့ရန်စာရင်း",
        "today_report": "📊 ဒီနေ့ Report",
        "settings": "⚙️ Settings / ဘာသာစကား",
        "back": "⬅️ နောက်သို့",
        "confirm": "✅ အတည်ပြု",
        "change": "✏️ ပြင်မယ်",
        "cancel": "❌ မလုပ်တော့ပါ",
        "ask_name": "Customer နာမည် ရိုက်ပါ။",
        "ask_phone": "ဖုန်းနံပါတ် ရိုက်ပါ။",
        "ask_item": "ပစ္စည်းအမည် ရိုက်ပါ။ ဥပမာ Dress, T-shirt",
        "ask_size": "အရွယ်အစား ရိုက်ပါ။ ဥပမာ S, M, L, XL, Free Size",
        "ask_color": "အရောင် ရိုက်ပါ။",
        "ask_amount": "ငွေပမာဏ ရိုက်ပါ။ ဥပမာ 45000",
        "ask_payment_status": "Payment Status ရွေးပါ။",
        "ask_payment_method": "Payment Method ရွေးပါ။",
        "ask_delivery_status": "Delivery Status ရွေးပါ။",
        "ask_note": "Address/Note ရိုက်ပါ။ မရှိရင် '-' လို့ရိုက်ပါ။",
        "invalid_amount": "ငွေပမာဏကို number နဲ့ပဲ ရိုက်ပါ။ ဥပမာ 45000",
        "preview_title": "အော်ဒါ စစ်ဆေးရန်",
        "correct_question": "အချက်အလက်မှန်ပါသလား?",
        "which_field": "ဘယ် field ကို ပြင်ချင်ပါသလဲ? Short key ရိုက်ပါ:",
        "invalid_key": "Short key မှားနေပါတယ် ❌\nCus, Ph, Item, Size, Color, Amt, Pay, Method, Del, Note ထဲက တစ်ခု ရိုက်ပါ။",
        "enter_new_value": "{field} အတွက် value အသစ် ရိုက်ပါ။",
        "saved": "သိမ်းပြီးပါပြီ ✅",
        "cancelled": "မလုပ်တော့ပါ။ Main menu ပြန်သွားပါမယ်။",
    },
}


def t(lang: str | None, key: str, **kwargs) -> str:
    lang = lang if lang in TEXT else "en"
    value = TEXT[lang].get(key, TEXT["en"].get(key, key))
    return value.format(**kwargs)
```

**Step 2: Add keyboard helper names**

Either in `i18n.py` or `bot.py`, create functions:

```python
def main_menu(lang: str): ...
def confirm_menu(lang: str): ...
def language_menu(): ...
def settings_menu(lang: str): ...
```

**Step 3: Verify import**

Run:

```bash
. .venv/bin/activate
python - <<'PY'
from src.i18n import t
print(t('en', 'add_order'))
print(t('my', 'add_order'))
PY
```

Expected:

```text
➕ Add Order
➕ အော်ဒါထည့်ရန်
```

---

### Task 3: Add order preview formatter with short keys

**Objective:** Show a clear order preview before saving.

**Files:**

- Modify: `/home/phyoshan8/automation-projects/telegram-clothing-order-bot/src/reports.py`

**Step 1: Add short key constants**

```python
EDIT_FIELDS = {
    "Cus": "Customer Name",
    "Ph": "Phone",
    "Item": "Item",
    "Size": "Size",
    "Color": "Color",
    "Amt": "Amount",
    "Pay": "Payment Status",
    "Method": "Payment Method",
    "Del": "Delivery Status",
    "Note": "Address/Note",
}

KEY_ALIASES = {key.lower(): key for key in EDIT_FIELDS}
```

**Step 2: Add validation helper**

```python
def normalize_edit_key(text: str) -> str | None:
    return KEY_ALIASES.get(text.strip().lower())
```

**Step 3: Add preview formatter**

```python
def order_preview(order: dict[str, str], lang: str = "en") -> str:
    lines = ["Order Preview" if lang == "en" else "အော်ဒါ စစ်ဆေးရန်", ""]
    lines.extend([
        f"Cus: {order.get('Customer Name', '-')}",
        f"Ph: {order.get('Phone', '-')}",
        f"Item: {order.get('Item', '-')}",
        f"Size: {order.get('Size', '-')}",
        f"Color: {order.get('Color', '-')}",
        f"Amt: {money(order.get('Amount', '0'))}",
        f"Pay: {order.get('Payment Status', '-')}",
        f"Method: {order.get('Payment Method', '-')}",
        f"Del: {order.get('Delivery Status', '-')}",
        f"Note: {order.get('Address/Note', '-')}",
    ])
    return "\n".join(lines)
```

**Step 4: Verify**

Run a small Python snippet to check `normalize_edit_key()` accepts `cus`, `CUS`, `Cus` and rejects `customer`.

Expected:

- `cus` -> `Cus`
- `CUS` -> `Cus`
- `customer` -> `None`

---

### Task 4: Refactor `/start` to require language choice first

**Objective:** If user language is unknown, ask language before showing main menu.

**Files:**

- Modify: `/home/phyoshan8/automation-projects/telegram-clothing-order-bot/src/bot.py`

**Step 1: Add language handlers**

Add message handlers for:

```text
English
မြန်မာ
```

When selected:

- call `set_user_language()`
- reply language saved
- show main menu in that language

**Step 2: Add helper `get_lang(update, context)`**

Pseudo-code:

```python
def get_lang(update, context) -> str | None:
    if "lang" in context.user_data:
        return context.user_data["lang"]
    settings = settings_from_context(context)
    lang = get_user_language(settings, update.effective_user.id)
    if lang:
        context.user_data["lang"] = lang
    return lang
```

**Step 3: Change `start()`**

Pseudo-code:

```python
async def start(update, context):
    lang = get_lang(update, context)
    if not lang:
        await update.message.reply_text(
            "Please choose language / ဘာသာစကားရွေးပါ",
            reply_markup=language_menu(),
        )
        return
    await update.message.reply_text(t(lang, 'welcome'), reply_markup=main_menu(lang))
```

**Step 4: Verify manually**

Use Telegram:

1. Send `/start` as a new user.
2. Bot asks language.
3. Choose English.
4. Bot shows English menu.
5. Change language later in settings.

---

### Task 5: Add Settings menu and language change

**Objective:** Let user change language later from menu.

**Files:**

- Modify: `src/bot.py`
- Modify: `src/i18n.py` if needed

**Step 1: Add Settings button handler**

When user taps Settings:

```text
Settings
[🌐 Language]
[⬅️ Back]
```

**Step 2: Add Language setting handler**

When user taps Language:

show language menu:

```text
[English]
[မြန်မာ]
```

**Step 3: On selection**

Update `User Settings` row and `context.user_data['lang']`.

**Step 4: Verify**

Manual test:

1. Set English.
2. Open Settings.
3. Change to Burmese.
4. Menu labels switch to Burmese.
5. Send `/start`; Burmese remains selected.

---

### Task 6: Change add-order flow to preview instead of immediate save

**Objective:** Stop saving immediately after Address/Note; show preview first.

**Files:**

- Modify: `src/bot.py`
- Modify: `src/reports.py`

**Step 1: Add new conversation states**

Current states end at `ASK_NOTE`. Add:

```python
ASK_CONFIRM,
ASK_EDIT_KEY,
ASK_EDIT_VALUE,
```

Because existing state constants use `range(10)`, update to `range(13)`.

**Step 2: Replace `save_order()` behavior**

Rename or change final note handler:

Current:

```python
async def save_order(...):
    append_order(...)
```

New:

```python
async def show_order_preview(update, context):
    context.user_data['order']['Address/Note'] = update.message.text.strip()
    lang = get_lang(update, context) or 'en'
    await update.message.reply_text(
        order_preview(context.user_data['order'], lang) + "\n\n" + t(lang, 'correct_question'),
        reply_markup=confirm_menu(lang),
    )
    return ASK_CONFIRM
```

**Step 3: Add confirm handler**

If Confirm:

- append order
- clear draft
- show saved confirmation
- return `ConversationHandler.END`

**Step 4: Add change handler**

If Change:

- show short key list
- return `ASK_EDIT_KEY`

**Step 5: Add cancel handler**

If Cancel:

- clear draft
- return main menu

**Step 6: Verify**

Manual test:

1. Add order.
2. Finish Note.
3. Confirm menu appears.
4. Check Google Sheet before confirm: no new row yet.
5. Tap Confirm.
6. Check Google Sheet: row appears.

---

### Task 7: Implement edit-by-short-key validation loop

**Objective:** Let user correct a field before saving and prevent wrong short keys.

**Files:**

- Modify: `src/bot.py`
- Modify: `src/reports.py`

**Step 1: Add valid key list message**

In `reports.py`, add:

```python
def edit_key_help(lang: str = 'en') -> str:
    ...
```

Include:

```text
Cus = Customer Name
Ph = Phone
Item = Item
Size = Size
Color = Color
Amt = Amount
Pay = Payment Status
Method = Payment Method
Del = Delivery Status
Note = Address/Note
```

**Step 2: Implement `receive_edit_key()`**

Pseudo-code:

```python
async def receive_edit_key(update, context):
    lang = get_lang(update, context) or 'en'
    key = normalize_edit_key(update.message.text)
    if not key:
        await update.message.reply_text(t(lang, 'invalid_key'))
        return ASK_EDIT_KEY
    context.user_data['edit_key'] = key
    field = EDIT_FIELDS[key]
    if key == 'Pay':
        await update.message.reply_text(t(lang, 'ask_payment_status'), reply_markup=PAYMENT_STATUS_MENU)
    elif key == 'Method':
        await update.message.reply_text(t(lang, 'ask_payment_method'), reply_markup=PAYMENT_METHOD_MENU)
    elif key == 'Del':
        await update.message.reply_text(t(lang, 'ask_delivery_status'), reply_markup=DELIVERY_STATUS_MENU)
    else:
        await update.message.reply_text(t(lang, 'enter_new_value', field=field), reply_markup=ReplyKeyboardRemove())
    return ASK_EDIT_VALUE
```

**Step 3: Implement `receive_edit_value()`**

Pseudo-code:

```python
async def receive_edit_value(update, context):
    lang = get_lang(update, context) or 'en'
    key = context.user_data['edit_key']
    field = EDIT_FIELDS[key]
    value = update.message.text.strip()

    if key == 'Amt' and not value.replace(',', '').isdigit():
        await update.message.reply_text(t(lang, 'invalid_amount'))
        return ASK_EDIT_VALUE

    context.user_data['order'][field] = value.replace(',', '') if key == 'Amt' else value
    context.user_data.pop('edit_key', None)

    await update.message.reply_text(
        order_preview(context.user_data['order'], lang) + "\n\n" + t(lang, 'correct_question'),
        reply_markup=confirm_menu(lang),
    )
    return ASK_CONFIRM
```

**Step 4: Verify wrong short key**

Manual test:

1. Add order.
2. Choose Change.
3. Type `Customer`.
4. Expected: error message, still waiting for key.
5. Type `Cus`.
6. Expected: asks for new Customer Name.
7. Enter value.
8. Preview updates.

---

### Task 8: Make option buttons language-safe

**Objective:** Ensure button text matching does not break when language changes.

**Files:**

- Modify: `src/bot.py`
- Modify: `src/i18n.py`

**Issue:**

Handlers currently match exact mixed text like:

```python
filters.Regex("^➕ Add Order / အော်ဒါထည့်ရန်$")
```

After localization, menu text changes.

**Preferred approach:**

Use regex that matches either language button text:

```python
filters.Regex("^(➕ Add Order|➕ အော်ဒါထည့်ရန်)$")
```

Or define constants for all accepted button texts.

**Step 1: Define button text sets**

In `i18n.py`:

```python
BUTTONS = {
    "add_order": {"➕ Add Order", "➕ အော်ဒါထည့်ရန်", "➕ Add Order / အော်ဒါထည့်ရန်"},
    ...
}
```

**Step 2: Add helper**

```python
def button_regex(name: str) -> str:
    import re
    return "^(" + "|".join(re.escape(x) for x in BUTTONS[name]) + ")$"
```

**Step 3: Use helper in `bot.py` handlers**

Example:

```python
MessageHandler(filters.Regex(button_regex('add_order')), begin_order)
```

**Verification:**

- English Add Order button works.
- Burmese Add Order button works.
- Old mixed button still works if present in old Telegram keyboard.

---

### Task 9: Add non-secret tests for pure logic

**Objective:** Test short-key validation and formatting without calling Telegram or Google.

**Files:**

- Create: `/home/phyoshan8/automation-projects/telegram-clothing-order-bot/tests/test_reports.py`
- Optional modify: `requirements.txt` to include `pytest`

**Step 1: Install pytest if needed**

```bash
cd /home/phyoshan8/automation-projects/telegram-clothing-order-bot
. .venv/bin/activate
pip install pytest
pip freeze > requirements.txt
```

**Step 2: Create tests**

```python
from src.reports import normalize_edit_key, order_preview


def test_normalize_edit_key_accepts_case_insensitive_keys():
    assert normalize_edit_key("cus") == "Cus"
    assert normalize_edit_key("CUS") == "Cus"
    assert normalize_edit_key(" Amt ") == "Amt"


def test_normalize_edit_key_rejects_unknown_key():
    assert normalize_edit_key("Customer") is None
    assert normalize_edit_key("Quantity") is None
    assert normalize_edit_key("Wrong") is None


def test_order_preview_includes_core_fields():
    preview = order_preview({
        "Customer Name": "May Thu",
        "Phone": "09911112222",
        "Item": "Dress",
        "Size": "M",
        "Color": "Black",
        "Amount": "45000",
        "Payment Status": "Unpaid",
        "Payment Method": "KPay",
        "Delivery Status": "Pending",
        "Address/Note": "Yangon",
    })
    assert "May Thu" in preview
    assert "Dress" in preview
    assert "45,000 MMK" in preview
```

**Step 3: Run tests**

```bash
. .venv/bin/activate
pytest -q
```

Expected:

```text
3 passed
```

---

### Task 10: Manual end-to-end validation

**Objective:** Prove the bot works through Telegram before reporting success.

**Files:**

- No new files.

**Step 1: Restart bot**

Kill existing background bot process if needed, then run:

```bash
cd /home/phyoshan8/automation-projects/telegram-clothing-order-bot
. .venv/bin/activate
python -m src.bot
```

**Step 2: Language test**

In Telegram:

1. Send `/start`.
2. If language unknown, choose English.
3. Confirm English menu appears.
4. Open Settings.
5. Change to Burmese.
6. Confirm Burmese menu appears.
7. Send `/start` again.
8. Confirm Burmese remains.

**Step 3: Confirm-before-save test**

1. Start Add Order.
2. Complete all fields.
3. When preview appears, check Google Sheet row count.
4. Confirm no new order saved yet.
5. Click Confirm.
6. Check Google Sheet row count increased by 1.

**Step 4: Edit valid key test**

1. Add another order.
2. Intentionally type wrong amount or wrong customer.
3. At preview, click Change.
4. Enter `Cus`.
5. Enter corrected customer name.
6. Preview shows corrected name.
7. Confirm and verify Sheet row has corrected name.

**Step 5: Edit invalid key test**

1. At edit key prompt, type `Quantity`.
2. Bot must reply with invalid key error.
3. Bot must continue waiting for correct key.
4. Type `Amt`.
5. Bot asks for amount.
6. Type non-number, e.g. `abc`.
7. Bot must reject and ask again.
8. Type `45000`.
9. Preview updates.

---

## Risks / Tradeoffs

### More conversation states means more bot complexity

The confirm/edit flow adds states and can introduce bugs if user presses old menu buttons mid-flow.

Mitigation:

- Keep `/cancel` working.
- Include Cancel button in preview.
- Use strict state handlers.

### Per-user language in Google Sheets may be slower

Reading language from Sheets on every message can be slow.

Mitigation:

- Cache language in `context.user_data['lang']` after first read.
- Only read from Sheet on `/start` or when missing in context.

### Button text matching can break after language switch

Mitigation:

- Centralize button labels in `i18n.py`.
- Use helper regex that accepts English, Burmese, and old mixed labels.

### Wrong short keys are expected user behavior

Mitigation:

- Do not treat wrong key as fatal.
- Return friendly error and ask again.
- Show accepted keys every time if needed.

---

## Open Questions

1. Should the first language default be English if user does not choose, or must choose before using bot?
   - Recommendation: must choose before using bot.

2. Should language be per Telegram user or global per shop?
   - Recommendation: per Telegram user using `User Settings` tab.

3. Should `Qty` be included even though current fields do not include Quantity?
   - User mentioned `Qty for Quantity`, but current confirmed fields do not include Quantity.
   - Recommendation: do not add Quantity now unless Shann confirms. For clothing sellers, Amount may be enough for follow-up. If needed later, add Quantity as a new field and Sheet column.

4. Should edit keys be Burmese too?
   - Recommendation: no. Use short English keys only because they are easier and unambiguous.

---

## Implementation Order Summary

1. Add `User Settings` tab and language storage.
2. Add `i18n.py` for English/Burmese text.
3. Add preview and edit-key helpers in `reports.py`.
4. Refactor `/start` for first language choice.
5. Add Settings language change.
6. Refactor add-order flow to preview before save.
7. Add edit-by-short-key loop and validation.
8. Fix button matching for localized labels.
9. Add pure logic tests.
10. Run full Telegram manual test.

---

## Immediate Next Step After This Plan

Ask Shann one clarification before implementation:

```text
You mentioned Qty for Quantity. Do you want to add Quantity as a real order field now?

A) No, keep current fields and use Amt only.
B) Yes, add Quantity field and a Qty edit key.
```

If Shann chooses A, implement the plan exactly as above.
If Shann chooses B, add `Quantity` between `Color` and `Amount`, update Orders headers, preview, edit keys, and conversation states.
