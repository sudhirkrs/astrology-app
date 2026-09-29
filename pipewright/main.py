"""HTTP API + single-page UI.  Run with:  uvicorn pipewright.main:app --reload"""

from __future__ import annotations

import html
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from pydantic import BaseModel

from .agent import MockAgent, get_agent
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

    @app.get("/api/meta")
    def meta():
        return {"agent": "demo" if isinstance(pw.agent, MockAgent) else "claude",
                "dry_run": pw.mailer.dry_run, "credits": CREDITS}

    @app.get("/api/campaigns")
    def campaigns():
        return pw.db.all("SELECT id, name, website, status, created_at FROM campaigns ORDER BY id DESC")

    @app.post("/api/campaigns")
    def create(body: CampaignIn):
        return run(pw.create_campaign, body.model_dump())

    @app.get("/api/campaigns/{cid}")
    def get(cid: int):
        return run(pw.campaign, cid)

    @app.patch("/api/campaigns/{cid}")
    def patch(cid: int, body: dict):
        return run(pw.update_campaign, cid, body)

    @app.get("/api/campaigns/{cid}/prospects")
    def prospects(cid: int):
        return pw.prospects(cid)

    @app.post("/api/campaigns/{cid}/prospects/discover")
    def discover(cid: int, body: Count):
        return run(pw.discover, cid, body.count)

    @app.post("/api/campaigns/{cid}/prospects/import")
    def import_csv(cid: int, body: CsvIn):
        return run(pw.import_csv, cid, body.csv)

    @app.put("/api/prospects/{pid}/email")
    def set_email(pid: int, body: EmailIn):
        return run(pw.set_prospect_email, pid, body.email)

    @app.post("/api/campaigns/{cid}/drafts")
    def draft(cid: int, body: Count):
        return run(pw.draft, cid, body.count)

    @app.get("/api/campaigns/{cid}/messages")
    def messages(cid: int, status: str | None = None):
        return pw.queue(cid, status)

    @app.patch("/api/messages/{mid}")
    def edit(mid: int, body: EditIn):
        return run(pw.edit_message, mid, body.subject, body.body)

    @app.post("/api/messages/{mid}/review")
    def review(mid: int, body: ReviewIn):
        return run(pw.review, mid, body.approve, body.whole_sequence)

    @app.post("/api/campaigns/{cid}/send")
    def send(cid: int):
        return run(pw.send, cid)

    @app.post("/api/campaigns/{cid}/replies")
    def reply(cid: int, body: ReplyIn):
        return run(pw.record_reply, cid, body.from_email, body.text)

    @app.get("/api/campaigns/{cid}/stats")
    def stats(cid: int):
        return {**pw.stats(cid), "ledger": pw.ledger(cid)}

    @app.get("/api/campaigns/{cid}/export.csv", response_class=PlainTextResponse)
    def export(cid: int):
        return PlainTextResponse(pw.export_csv(cid), media_type="text/csv",
                                 headers={"Content-Disposition": f'attachment; filename="campaign-{cid}.csv"'})

    @app.api_route("/u/{token}", methods=["GET", "POST"], include_in_schema=False)
    def unsubscribe(token: str):
        email = pw.unsubscribe(token)
        msg = f"{html.escape(email)} has been unsubscribed. You won't hear from us again." if email else "This link is invalid."
        return HTMLResponse(f"<!doctype html><meta name=viewport content='width=device-width'>"
                            f"<body style='font-family:system-ui;padding:2rem'><p>{msg}</p></body>")

    return app


app = create_app()
