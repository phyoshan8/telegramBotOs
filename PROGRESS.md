# Progress Log — Telegram Clothing Order Bot

Last updated: 2026-06-21 13:51:28 +0630

## Project goal

Build a Telegram-first clothing order tracker for Myanmar online sellers.

Client-facing UX:
- Seller uses Telegram buttons, not raw Google Sheet rows or Google Form links.
- Bot collects clothing order details.
- Bot shows unpaid/COD/deposit list, pending delivery list, and today report.

Backend:
- Python Telegram bot.
- Google Sheets as database.
- One bot/config per client for first version.

## Current implementation status

Done:

1. Project scaffold created
   - Path: `/home/phyoshan8/automation-projects/telegram-clothing-order-bot`
   - Main source path: `src/`

2. Python environment created
   - Venv: `.venv/`
   - Important dependency install command:
     ```bash
     cd /home/phyoshan8/automation-projects/telegram-clothing-order-bot
     . .venv/bin/activate
     pip install -r requirements.txt
     ```

3. Google Sheets backend connected
   - Spreadsheet ID: `1LqS-SNur3NlGI1RzEmxclzj0__ZuZrHKW75I0Awht1c`
   - Orders tab: `Orders`
   - Service account JSON path: `/home/phyoshan8/Downloads/gen-lang-client-0421887141-7ac567df0f93.json`
   - Service account email used for Sheet sharing:
     `ais-gemini-key-eef8e2d4e589418@828561949308.iam.gserviceaccount.com`

4. Google APIs enabled
   - Google Sheets API enabled.
   - Google Drive API enabled.
   - Project: `gen-lang-client-0421887141`

5. Bot token configured in `.env`
   - Do not print or commit `.env`.
   - The original token was pasted in chat, so it is exposed.
   - Regenerate before real customers.

6. Sheet setup command works
   ```bash
   cd /home/phyoshan8/automation-projects/telegram-clothing-order-bot
   . .venv/bin/activate
   python -m src.sheet_setup
   ```

7. Orders tab headers now include Quantity
   ```text
   ID, Date, Customer Name, Phone, Item, Size, Color, Quantity, Amount,
   Payment Status, Payment Method, Delivery Status, Address/Note,
   Status, Created At, Updated At
   ```

8. User language settings added
   - Tab: `User Settings`
   - Headers:
     ```text
     Telegram User ID, Username, First Name, Language, Updated At
     ```

9. Bot supports language selection
   - First start can ask for English or Burmese.
   - Language is stored per Telegram user.
   - Language can be changed from Settings.

10. Bot supports confirm-before-save
    - After collecting order data, bot shows preview.
    - User can Confirm or Change.
    - Order is saved to Google Sheets only after Confirm.

11. Bot supports edit-by-short-key
    - Valid edit keys:
      ```text
      Cus, Ph, Item, Size, Color, Qty, Amt, Pay, Method, Del, Note
      ```
    - Wrong keys like `Quantity`, `Customer`, `abc` are rejected.
    - Quantity and Amount are number-validated.

12. Automated tests added
    - Test file: `tests/test_reports.py`
    - Current passing output:
      ```text
      3 passed in 0.01s
      ```

13. Bot is currently running in background
    - Process session ID: `proc_20112ff49861`
    - Command:
      ```bash
      . .venv/bin/activate && python -m src.bot
      ```

## Current bot flow

Fields collected:

1. Customer Name
2. Phone
3. Item
4. Size
5. Color
6. Quantity
7. Amount
8. Payment Status
9. Payment Method
10. Delivery Status
11. Address/Note

Payment Status options:
- Paid
- Unpaid
- COD
- Deposit

Payment Method options:
- KPay
- Wave
- AYA Pay
- CB Pay
- Cash
- Other

Delivery Status options:
- Pending
- Delivered
- Pickup
- Cancelled
- Returned

Main menu buttons:
- Add Order
- Unpaid List
- Pending Delivery
- Today Report
- Settings

## Manual test still needed from user

In Telegram:

1. Send `/start`.
2. Choose language if asked.
3. Tap Add Order.
4. Enter test order:
   ```text
   Customer Name: May Thu
   Phone: 09911112222
   Item: Dress
   Size: M
   Color: Black
   Quantity: 2
   Amount: 45000
   Payment Status: Unpaid
   Payment Method: KPay
   Delivery Status: Pending
   Address/Note: Yangon
   ```
5. At preview, tap Change.
6. Type wrong key: `Quantity`.
   - Expected: invalid key error.
7. Type correct key: `Qty`.
8. Enter `3`.
   - Expected: preview updates Qty to 3.
9. Tap Confirm.
   - Expected: only now row is saved to Google Sheet.
10. Test Unpaid List, Pending Delivery, Today Report.

## Known warnings / quirks

1. `Regional Access Boundary HTTP request failed... FAILED_PRECONDITION`
   - This warning appeared during gspread/Google calls.
   - Despite warning, Sheet setup and row append succeeded.
   - Do not treat it as fatal unless the command exits non-zero.

2. Exposed Telegram token
   - Current token was pasted in chat.
   - OK for temporary demo only.
   - Must regenerate in BotFather before real customer use.

3. Existing verification row
   - A test row may exist in Orders:
     `C-0001 Test Customer ...`
   - It was created to verify Google Sheets writing.
   - Safe to delete manually from Sheet if it pollutes demo data.

## Next recommended steps

1. Complete Telegram manual test.
2. If manual test passes, record a 2-minute demo video.
3. Regenerate Telegram bot token before showing to real customers.
4. Add deployment plan for GCP VM/systemd.
5. Later add client setup automation:
   - copy Google Sheet template
   - write `.env` per client
   - create systemd service per client

## Do not forget

This project is a managed-service prototype:
- Shann owns code/template.
- Client uses Telegram bot only.
- Client data can live in their own Google Sheet.
- One client = one bot token + one Google Sheet + one `.env` for now.
