"""HTTP API + single-page UI.  Run with:  uvicorn pipewright.main:app --reload"""

from __future__ import annotations

import hmac
import html
import os
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from pydantic import BaseModel

from . import auth
from .agent import MockAgent, get_agent
from .auth import current_user
from .db import DB
from .service import CREDITS, Pipewright, WorkflowError

STATIC = Path(__file__).parent / "static"


class CampaignIn(BaseModel):
    website: str = ""
    description: str = ""
    name: str | None = None
    sender_name: str | None = None
    sender_email: str | None = None
    sender_company: str | None = None
    postal_address: str | None = None
    booking_link: str | None = None
    crm_webhook: str | None = None
    daily_cap: int = 30
    mailbox_age_days: int = 0
    autopilot: bool = False
    autopilot_min_score: int = 85


class Count(BaseModel):
    count: int = 10


class CsvIn(BaseModel):
    csv: str


class EmailIn(BaseModel):
    email: str


class EditIn(BaseModel):
    subject: str | None = None
    body: str | None = None


class ReviewIn(BaseModel):
    approve: bool
    whole_sequence: bool = True


class ReplyIn(BaseModel):
    from_email: str
    text: str


def create_app(pw: Pipewright | None = None) -> FastAPI:
    if pw is None:
        agent = get_agent()
        # demo data uses reserved .example domains, which have no MX records
        pw = Pipewright(DB(), agent, check_dns=not isinstance(agent, MockAgent))
    app = FastAPI(title="Pipewright", version="0.1.0")

    def run(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except WorkflowError as e:
            raise HTTPException(400, str(e)) from e

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(STATIC / "index.html")

    def own(user: dict, **ids) -> None:
        if not pw.owns(user["id"], **ids):
            raise HTTPException(404, "not found")

    @app.get("/api/health")
    def health():
        """Public liveness check: confirms the database answers. Never returns data."""
        try:
            pw.db.one("SELECT 1 AS ok")
            db_ok = True
        except Exception:
            db_ok = False
        return {"ok": db_ok, "db": "postgres" if pw.db.pg else "sqlite",
                "agent": "demo" if isinstance(pw.agent, MockAgent) else "claude", "auth": auth.enabled()}

    @app.get("/api/config")
    def config():
        """Public: what the browser needs to start sign-in."""
        return {"auth": auth.enabled(), "supabase_url": auth.SUPABASE_URL, "supabase_anon_key": auth.SUPABASE_ANON_KEY}

    @app.get("/api/meta")
    def meta(user: dict = Depends(current_user)):
        return {"agent": "demo" if isinstance(pw.agent, MockAgent) else "claude",
                "dry_run": pw.mailer.dry_run, "credits": CREDITS, "user": user["email"]}

    @app.get("/api/campaigns")
    def campaigns(user: dict = Depends(current_user)):
        return pw.campaigns(user["id"])

    @app.post("/api/campaigns")
    def create(body: CampaignIn, user: dict = Depends(current_user)):
        return run(pw.create_campaign, body.model_dump(), user["id"])

    @app.get("/api/campaigns/{cid}")
    def get(cid: int, user: dict = Depends(current_user)):
        own(user, campaign_id=cid)
        return run(pw.campaign, cid)

    @app.patch("/api/campaigns/{cid}")
    def patch(cid: int, body: dict, user: dict = Depends(current_user)):
        own(user, campaign_id=cid)
        body.pop("owner_id", None)
        return run(pw.update_campaign, cid, body)

    @app.get("/api/campaigns/{cid}/prospects")
    def prospects(cid: int, user: dict = Depends(current_user)):
        own(user, campaign_id=cid)
        return pw.prospects(cid)

    @app.post("/api/campaigns/{cid}/prospects/discover")
    def discover(cid: int, body: Count, user: dict = Depends(current_user)):
        own(user, campaign_id=cid)
        return run(pw.discover, cid, body.count)

    @app.post("/api/campaigns/{cid}/prospects/import")
    def import_csv(cid: int, body: CsvIn, user: dict = Depends(current_user)):
        own(user, campaign_id=cid)
        return run(pw.import_csv, cid, body.csv)

    @app.put("/api/prospects/{pid}/email")
    def set_email(pid: int, body: EmailIn, user: dict = Depends(current_user)):
        own(user, prospect_id=pid)
        return run(pw.set_prospect_email, pid, body.email)

    @app.post("/api/campaigns/{cid}/drafts")
    def draft(cid: int, body: Count, user: dict = Depends(current_user)):
        own(user, campaign_id=cid)
        return run(pw.draft, cid, body.count)

    @app.get("/api/campaigns/{cid}/messages")
    def messages(cid: int, status: str | None = None, user: dict = Depends(current_user)):
        own(user, campaign_id=cid)
        return pw.queue(cid, status)

    @app.patch("/api/messages/{mid}")
    def edit(mid: int, body: EditIn, user: dict = Depends(current_user)):
        own(user, message_id=mid)
        return run(pw.edit_message, mid, body.subject, body.body)

    @app.post("/api/messages/{mid}/review")
    def review(mid: int, body: ReviewIn, user: dict = Depends(current_user)):
        own(user, message_id=mid)
        return run(pw.review, mid, body.approve, body.whole_sequence)

    @app.post("/api/campaigns/{cid}/send")
    def send(cid: int, user: dict = Depends(current_user)):
        own(user, campaign_id=cid)
        return run(pw.send, cid)

    @app.post("/api/campaigns/{cid}/replies")
    def reply(cid: int, body: ReplyIn, user: dict = Depends(current_user)):
        own(user, campaign_id=cid)
        return run(pw.record_reply, cid, body.from_email, body.text)

    @app.get("/api/campaigns/{cid}/stats")
    def stats(cid: int, user: dict = Depends(current_user)):
        own(user, campaign_id=cid)
        return {**pw.stats(cid), "ledger": pw.ledger(cid)}

    @app.get("/api/campaigns/{cid}/export.csv", response_class=PlainTextResponse)
    def export(cid: int, user: dict = Depends(current_user)):
        own(user, campaign_id=cid)
        return PlainTextResponse(pw.export_csv(cid), media_type="text/csv",
                                 headers={"Content-Disposition": f'attachment; filename="campaign-{cid}.csv"'})

    @app.get("/api/cron/send", include_in_schema=False)
    def cron_send(authorization: str | None = Header(default=None)):
        """Vercel Cron calls this daily with `Authorization: Bearer $CRON_SECRET`."""
        secret = os.environ.get("CRON_SECRET")
        if not secret or not hmac.compare_digest(authorization or "", f"Bearer {secret}"):
            raise HTTPException(401, "unauthorized")
        return {"results": pw.send_all_due()}

    @app.api_route("/u/{token}", methods=["GET", "POST"], include_in_schema=False)
    def unsubscribe(token: str):
        email = pw.unsubscribe(token)
        msg = f"{html.escape(email)} has been unsubscribed. You won't hear from us again." if email else "This link is invalid."
        return HTMLResponse(f"<!doctype html><meta name=viewport content='width=device-width'>"
                            f"<body style='font-family:system-ui;padding:2rem'><p>{msg}</p></body>")

    return app


app = create_app()
