# Telegram Clothing Order Bot

Telegram bot for Myanmar clothing online sellers.

Customer-facing UX:
- Telegram buttons, not raw spreadsheet editing.
- English/Burmese language choice.
- Confirm-before-save order preview.
- Short-key edit flow for fixing mistakes before saving.

Backend:
- Python Telegram bot.
- Google Sheets database.
- One bot/config per client for first managed-service version.

## First MVP

- Add clothing order
- Choose English/Burmese language
- Change language later from Settings
- Preview order before saving
- Edit wrong fields using short keys
- Show unpaid/COD/deposit list
- Show pending delivery list
- Show today report

## Project files

```text
src/bot.py             Telegram bot conversation flow
src/config.py          Loads .env settings
src/storage_sheets.py  Google Sheets setup/read/write/report data logic
src/reports.py         Message formatting, preview, edit-key validation
src/i18n.py            English/Burmese labels and keyboards
src/sheet_setup.py     Initializes Google Sheet tabs/headers
tests/test_reports.py  Pure logic tests
PROGRESS.md            Current state and handoff notes
MAINTENANCE.md         Troubleshooting and maintenance guide
```

## Security

- Never hardcode Telegram bot tokens.
- Store secrets in `.env` only.
- `.env` and Google service account JSON files must not be committed.
- The current token was pasted in chat, so regenerate before real customers.

## Run

```bash
cd /home/phyoshan8/automation-projects/telegram-clothing-order-bot
. .venv/bin/activate
python -m src.sheet_setup
python -m src.bot
```

## Test

```bash
cd /home/phyoshan8/automation-projects/telegram-clothing-order-bot
. .venv/bin/activate
python -m py_compile src/*.py
pytest -q
```

## Current status

See:

```text
PROGRESS.md
MAINTENANCE.md
```
