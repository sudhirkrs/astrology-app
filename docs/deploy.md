# Deploying Pipewright (Vercel + Supabase)

```
browser ──magic link──► Supabase Auth
   │  Bearer JWT
   ▼
Vercel (FastAPI function, region bom1)  ──pooler :6543──►  Supabase Postgres (ap-south-1)
   ▲                                                         RLS on; only role pipewright_app has a policy
Vercel Cron 03:30 UTC daily → /api/cron/send (Bearer CRON_SECRET)
```

## Already done

- Supabase project **pipewright** (`wharmuahehhxdvhjjarm`, Mumbai), created in the *finostock* org.
- Migrations applied: `supabase/migrations/*` (tables, indexes, RLS, least-privilege `pipewright_app` role).
- The app role's password was set out-of-band and is kept only in the Vercel env vars.
- Repo contains `vercel.json` (function config, 300s max duration, daily cron) and `api/index.py`.

## Remaining steps

1. **Create the Vercel project.** Go to vercel.com/new, import `sudhirkrs/astrology-app`, and use the project name `pipewright`. Framework: FastAPI or Other; no build command is needed.
2. **Environment variables.** Paste the prepared env file into Settings → Environment Variables. These are the variables:

   | Key | Purpose |
   |---|---|
   | `DATABASE_URL` | Supabase transaction pooler as `pipewright_app.<ref>`. Two hosts are separated by a space, and the app uses whichever connects |
   | `PIPEWRIGHT_SKIP_MIGRATE=1` | The schema is managed by Supabase migrations |
   | `SUPABASE_URL`, `SUPABASE_ANON_KEY` | Sign-in. The publishable key is safe in the browser |
   | `PIPEWRIGHT_ALLOWED_EMAILS` | Who may sign in: comma-separated addresses or `@domain.com` |
   | `PIPEWRIGHT_SECRET` | HMAC key for unsubscribe links |
   | `CRON_SECRET` | Vercel sends it to the daily cron endpoint |
   | `PIPEWRIGHT_BASE_URL` | Public URL, used in unsubscribe links |
   | `ANTHROPIC_API_KEY` | Turns on the real Claude agent. Without it the app runs the demo agent |
   | `PIPEWRIGHT_SMTP_HOST/PORT/USER/PASSWORD` | Optional: real sending from your mailbox. Without them, sends are dry-run |

3. **Function region:** Settings → Functions → Region → **Mumbai (bom1)**. This keeps the app next to the database.
4. **Supabase Auth URLs:** Authentication → URL Configuration. Set **Site URL** to the Vercel URL and add it under **Redirect URLs**, otherwise magic links point to localhost.
5. **Deploy**, then open `https://<your-app>/api/health` and expect `{"ok": true, "db": "postgres", ...}`.

## Operating it

- Every push to the connected branch redeploys automatically. Pull-request branches get preview URLs.
- Sending: the daily cron sends whatever is due (approved first touches, due follow-ups and approved replies) within each campaign's warm-up cap. The **Send what's due** button still works any time.
- Logs: Vercel → Deployments → Functions logs. Supabase → Logs (`postgres_logs`, `supavisor_logs`).
- Rotate the DB password: `ALTER ROLE pipewright_app PASSWORD '…'` in the Supabase SQL editor, then update `DATABASE_URL` in Vercel and redeploy.
