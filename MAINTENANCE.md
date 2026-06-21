# Maintenance Guide — Telegram Clothing Order Bot

This file is for future agents and for Shann when troubleshooting later.

## Quick project facts

Project path:

```bash
/home/phyoshan8/automation-projects/telegram-clothing-order-bot
```

Main files:

```text
src/bot.py             Telegram bot conversation flow
src/config.py          Loads .env settings
src/storage_sheets.py  Google Sheets setup/read/write/report data logic
src/reports.py         Message formatting, preview, edit-key validation
src/i18n.py            English/Burmese labels and keyboards
src/sheet_setup.py     Initializes Google Sheet tabs/headers
tests/test_reports.py  Pure logic tests
.env                   Secrets/config, never commit
```

## Current runtime

Bot may be running in Hermes background process:

```text
proc_20112ff49861
```

Check:

```bash
# From Hermes process tool, poll proc_20112ff49861
```

If using terminal only, find Python bot process:

```bash
ps aux | grep 'python -m src.bot' | grep -v grep
```

Stop from shell:

```bash
pkill -f 'python -m src.bot'
```

Start manually:

```bash
cd /home/phyoshan8/automation-projects/telegram-clothing-order-bot
. .venv/bin/activate
python -m src.bot
```

## Run setup/checks

Activate venv:

```bash
cd /home/phyoshan8/automation-projects/telegram-clothing-order-bot
. .venv/bin/activate
```

Compile check:

```bash
python -m py_compile src/*.py
```

Run tests:

```bash
pytest -q
```

Initialize Google Sheet:

```bash
python -m src.sheet_setup
```

## Environment variables

`.env` should contain:

```env
TELEGRAM_BOT_TOKEN=...
GOOGLE_SHEET_ID=1LqS-SNur3NlGI1RzEmxclzj0__ZuZrHKW75I0Awht1c
GOOGLE_SERVICE_ACCOUNT_FILE=/home/phyoshan8/Downloads/gen-lang-client-0421887141-7ac567df0f93.json
GOOGLE_SHEET_TAB=Orders
TIMEZONE=Asia/Yangon
```

Never print the full token in final responses.

## Google Sheets access

Service account email:

```text
ais-gemini-key-eef8e2d4e589418@828561949308.iam.gserviceaccount.com
```

The Google Sheet must be shared with this email as Editor.

Google Cloud project:

```text
gen-lang-client-0421887141
```

APIs needed:

```text
sheets.googleapis.com
drive.googleapis.com
```

Enable if needed:

```bash
gcloud services enable sheets.googleapis.com drive.googleapis.com --project gen-lang-client-0421887141
```

## Sheet tabs

The setup script should create/verify:

```text
Orders
Dashboard
Unpaid
Pending Delivery
Settings
User Settings
```

Orders headers:

```text
ID
Date
Customer Name
Phone
Item
Size
Color
Quantity
Amount
Payment Status
Payment Method
Delivery Status
Address/Note
Status
Created At
Updated At
```

User Settings headers:

```text
Telegram User ID
Username
First Name
Language
Updated At
```

## Core design logic

### Why `.env`

Tokens and Sheet IDs must not be hardcoded. For future clients, copy the same codebase and change only `.env`.

### Why Google Sheets service account

The bot is not Shann’s Gmail. It acts as a robot Google account. The Sheet owner must share the Sheet with the service account email.

### Why confirm-before-save

Small sellers may mistype on phone. The bot must not write wrong rows immediately. It collects a draft, previews it, then saves only after Confirm.

### Why short edit keys

Short keys are predictable:

```text
Cus, Ph, Item, Size, Color, Qty, Amt, Pay, Method, Del, Note
```

Wrong long words are rejected. This prevents bot guessing the wrong field.

### Why per-user language

A shop may have multiple admins. Each Telegram user can use English or Burmese independently.

## Troubleshooting

### Bot does not reply

1. Check bot process is running.
2. Check token in `.env` is valid.
3. If token was regenerated in BotFather, update `.env` and restart bot.
4. Check logs from background process or foreground terminal.

### Google Sheet permission error

Symptoms:

```text
403 permission denied
SpreadsheetNotFound
```

Fix:

1. Confirm service account JSON path exists.
2. Get service account email from JSON:
   ```bash
   python3 - <<'PY'
   import json
   p='/home/phyoshan8/Downloads/gen-lang-client-0421887141-7ac567df0f93.json'
   print(json.load(open(p))['client_email'])
   PY
   ```
3. Share the Google Sheet with that email as Editor.
4. Run:
   ```bash
   . .venv/bin/activate
   python -m src.sheet_setup
   ```

### Google Sheets API disabled

Symptom:

```text
Google Sheets API has not been used ... or it is disabled
```

Fix:

```bash
gcloud services enable sheets.googleapis.com drive.googleapis.com --project gen-lang-client-0421887141
```

### Regional Access Boundary warning

Symptom:

```text
Regional Access Boundary HTTP request failed after retries: ... FAILED_PRECONDITION
```

Observed behavior:
- Warning appeared but operations still succeeded.
- Treat as non-fatal if exit code is 0 and Sheet changes happen.

### Wrong short key issue

Expected behavior:
- If user types `Quantity`, `Customer`, or `wrong`, bot rejects.
- User must type `Qty`, `Cus`, etc.

Test:

```bash
. .venv/bin/activate
pytest tests/test_reports.py -q
```

### Quantity/Amount validation

Expected:
- Quantity must be digits, e.g. `2`.
- Amount must be digits, e.g. `45000`.
- Commas are stripped, so `45,000` is accepted.

## Safe change workflow for future agents

1. Stop running bot before editing:
   ```bash
   pkill -f 'python -m src.bot'
   ```

2. Update tests first for logic changes.

3. Run failing test if adding behavior.

4. Implement change.

5. Run:
   ```bash
   . .venv/bin/activate
   python -m py_compile src/*.py
   pytest -q
   python -m src.sheet_setup
   ```

6. Restart bot:
   ```bash
   . .venv/bin/activate
   python -m src.bot
   ```

7. Manually test in Telegram.

## Security checklist before real customers

- Regenerate bot token in BotFather because current token was exposed in chat.
- Update `.env` with new token.
- Restart bot.
- Use a separate Google Sheet per client.
- Do not mix client data.
- Do not commit `.env` or JSON credentials.
- Prefer client-owned Google Sheet shared to service account.

## Future improvements

1. Add update existing order status command.
2. Add Done/Delivered update flow.
3. Add daily scheduled Telegram summary.
4. Add low stock / variation tracking.
5. Add GCP VM deployment with systemd.
6. Add new-client setup script:
   - copy Sheet template
   - create `.env`
   - run `sheet_setup`
   - start systemd service
