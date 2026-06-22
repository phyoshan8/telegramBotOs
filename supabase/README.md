# Supabase setup

Supabase is the primary database for the scalable version of this bot.
Google Sheets/Excel should be treated as export targets only.

## Setup steps

1. Create a Supabase project.
2. Open Supabase SQL Editor.
3. Run `supabase/schema.sql` from this repo.
4. Copy the Project URL into `.env` as `SUPABASE_URL`.
5. Copy the service role key into `.env` as `SUPABASE_SERVICE_ROLE_KEY`.
6. Set:

```env
STORAGE_BACKEND=supabase
```

7. Restart the bot.

## Security rule

`SUPABASE_SERVICE_ROLE_KEY` is server-only.

Safe:

- Telegram bot running on your VM/server
- local backend scripts
- private cloud service environment variables

Not safe:

- browser frontend
- public JavaScript
- committed files
- GitHub repo

## Admin role

Telegram admin panel should use `user_settings.role`.

Roles:

- `seller`: normal order entry and basic views
- `admin`: admin panel, reports, export, and future update actions

Future admin actions should keep approve/cancel confirmation before changing important data.
