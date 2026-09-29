# Pipewright: the AI SDR that never emails anyone without your OK

Pipewright is an AI outbound agent in the same category as [Explee AutoGTM](https://explee.com/). It is built around the things Explee users complain about: agents that send on their own, shared inboxes, locked-in data and opaque billing.

```
website / one-liner ─► ICP research ─► prospects with buying signals ─► personalized 3-step sequences
                                                                              │
          CRM webhook ◄─ reply triage + drafted response ◄─ send from YOUR mailbox ◄─ human approval
```

- **Business docs:** [competitive analysis of Explee](docs/competitive-analysis.md) · [launch and marketing plan](docs/launch-and-marketing-plan.md)

## What it does

| Step | How |
|---|---|
| 1. ICP | Claude researches your website with web search and fetch, then returns a structured, editable ideal customer profile |
| 2. Prospects | Claude searches the web for real companies that match the ICP *and* show a buying signal (hiring, funding, launches). You get a fit score, the reason it fits and a public decision maker. Or import a CSV |
| 3. Emails | Likely address from common patterns, MX check, and flags for role, disposable and invalid addresses |
| 4. Copy | A personalized first email plus 2 follow-ups, each showing the fact it relies on. Linted for spam triggers, length and links |
| 5. Approval | **Nothing is sent until you approve it.** Optional autopilot only covers prospects with a high fit score, a verified email and clean copy |
| 6. Send | Through your own SMTP mailbox (dry-run outbox by default). Enforced warm-up ramp and daily cap, `List-Unsubscribe` one-click header, compliance footer with postal address |
| 7. Replies | Claude classifies intent (interested, meeting, question, not now, unsubscribe, OOO…). Any real reply stops the sequence. Unsubscribes are suppressed. A drafted response waits for your approval. Interested leads go to your CRM webhook |
| 8. Reporting | Reply rate, interested leads, a credit ledger per action, credits per interested lead, and CSV export |

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# Demo mode: deterministic fake data, no API key, emails go to outbox.jsonl
PIPEWRIGHT_MOCK=1 .venv/bin/uvicorn pipewright.main:app --reload
# open http://localhost:8000

# Real agent: uses Claude with web search/fetch
export ANTHROPIC_API_KEY=sk-ant-...
.venv/bin/uvicorn pipewright.main:app
```

Tests: `.venv/bin/python -m pytest -q`

### Configuration

| Env var | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | – | Enables the Claude agent (otherwise demo mode) |
| `PIPEWRIGHT_MODEL` | `claude-opus-5-5` | Model for research, copy and triage |
| `PIPEWRIGHT_MOCK` | – | `1` forces demo mode |
| `PIPEWRIGHT_SMTP_HOST` / `_PORT` / `_USER` / `_PASSWORD` | – | Your mailbox. Unset means dry-run to `PIPEWRIGHT_OUTBOX` |
| `PIPEWRIGHT_DB` | `pipewright.db` | SQLite file |
| `PIPEWRIGHT_BASE_URL` | `http://localhost:8000` | Used in unsubscribe links |
| `PIPEWRIGHT_SECRET` | dev value | HMAC key for unsubscribe tokens. **Set it in production** |

## Code map

| File | Role |
|---|---|
| `pipewright/agent.py` | `ClaudeAgent` (web research plus structured outputs, with server-side refusal fallback) and `MockAgent` |
| `pipewright/schemas.py` | Pydantic shapes for the ICP, prospects, email drafts and reply analysis |
| `pipewright/service.py` | Campaign workflow, approval rules, send scheduling, reply handling, credit ledger |
| `pipewright/deliverability.py` | Email guessing and verification, copy linting, warm-up ramp, compliance footer |
| `pipewright/mailer.py` | SMTP or dry-run outbox with RFC 8058 unsubscribe headers |
| `pipewright/main.py` | FastAPI routes and `/u/{token}` unsubscribe |
| `pipewright/static/index.html` | Single-page UI |

## API

`POST /api/campaigns` · `PATCH /api/campaigns/{id}` · `POST /api/campaigns/{id}/prospects/discover` · `POST /api/campaigns/{id}/prospects/import` · `POST /api/campaigns/{id}/drafts` · `GET /api/campaigns/{id}/messages?status=` · `PATCH /api/messages/{id}` · `POST /api/messages/{id}/review` · `POST /api/campaigns/{id}/send` · `POST /api/campaigns/{id}/replies` · `GET /api/campaigns/{id}/stats` · `GET /api/campaigns/{id}/export.csv`. Interactive docs are at `/docs`.

## MVP limits and roadmap to a hosted product

This is a single-tenant MVP. Before public launch (see the plan's Phase 0):

- Auth, multi-tenancy, Postgres, and billing (Stripe or Razorpay)
- Gmail/Outlook OAuth mailbox connection and IMAP reply ingestion (today, replies are posted to the API or pasted in the UI)
- A scheduled daily send job (today you trigger **Send what's due**), bounce processing, auto-pause when bounces exceed 3%, and credit refunds for hard bounces
- A verified contact-data provider next to AI research (guessed emails are marked `unknown` until DNS or a verifier confirms them)
- Region-aware compliance rules (GDPR legitimate-interest checks for EU contacts)
