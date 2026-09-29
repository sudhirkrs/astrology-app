from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from pipewright import deliverability as dv
from pipewright.agent import MockAgent
from pipewright.db import DB
from pipewright.main import create_app
from pipewright.service import Pipewright, WorkflowError, email_from_token, unsubscribe_token


class FakeMailer:
    dry_run = True

    def __init__(self):
        self.sent = []

    def send(self, sender, to, subject, body, unsubscribe_url):
        self.sent.append({"to": to, "subject": subject, "body": body})


@pytest.fixture
def pw(tmp_path):
    return Pipewright(DB(str(tmp_path / "t.db")), MockAgent(), FakeMailer(), check_dns=False)


def make_campaign(pw, **kw):
    data = {"website": "https://acme.example", "description": "AI SDR for SaaS", "sender_name": "Asha",
            "sender_email": "asha@acme.example", "sender_company": "Acme", "postal_address": "1 Main St, Pune",
            "booking_link": "https://cal.example/asha", "daily_cap": 30, "mailbox_age_days": 30, **kw}
    return pw.create_campaign(data)


def test_full_flow_requires_approval_before_sending(pw):
    c = make_campaign(pw)
    prospects = pw.discover(c["id"], 5)
    assert len(prospects) == 5
    assert all(p["email"] or p["email_status"] == "missing" for p in prospects)

    drafts = pw.draft(c["id"])
    assert drafts and all(d["status"] == "pending_review" for d in drafts)
    assert pw.send(c["id"])["sent"] == 0  # nothing approved yet

    pw.review(drafts[0]["id"], approve=True)
    result = pw.send(c["id"])
    assert result["sent"] == 1
    assert "unsubscribe" in pw.mailer.sent[0]["body"].lower()
    assert "1 Main St" in pw.mailer.sent[0]["body"]


def test_followups_wait_and_stop_on_reply(pw):
    c = make_campaign(pw)
    pw.discover(c["id"], 1)
    first = pw.draft(c["id"])[0]
    pw.review(first["id"], approve=True)
    t0 = datetime(2026, 9, 1, 9, tzinfo=timezone.utc)
    assert pw.send(c["id"], t0)["sent"] == 1
    assert pw.send(c["id"], t0 + timedelta(days=1))["sent"] == 0  # follow-up not due yet
    assert pw.send(c["id"], t0 + timedelta(days=3))["sent"] == 1  # follow-up #1

    email = pw.db.get("prospects", first["prospect_id"])["email"]
    out = pw.record_reply(c["id"], email, "Sounds good, can we set up a call next week?")
    assert out["analysis"]["intent"] == "meeting_request"
    assert out["prospect"]["status"] == "interested"
    assert out["draft_reply"]["status"] == "pending_review"
    # follow-up #2 is cancelled once they reply
    assert pw.send(c["id"], t0 + timedelta(days=20))["sent"] == 0


def test_unsubscribe_suppresses_future_sends(pw):
    c = make_campaign(pw)
    pw.discover(c["id"], 1)
    first = pw.draft(c["id"])[0]
    email = pw.db.get("prospects", first["prospect_id"])["email"]
    pw.review(first["id"], approve=True)
    assert pw.unsubscribe(unsubscribe_token(email)) == email
    assert pw.send(c["id"])["sent"] == 0
    assert pw.db.is_suppressed(email)


def test_token_tamper_rejected():
    tok = unsubscribe_token("a@b.co")
    assert email_from_token(tok) == "a@b.co"
    assert email_from_token(tok[:-1] + ("0" if tok[-1] != "0" else "1")) is None
    assert email_from_token("garbage") is None


def test_autopilot_only_when_opted_in(pw):
    c = make_campaign(pw, autopilot=True, autopilot_min_score=80)
    pw.discover(c["id"], 4)
    # without DNS checks emails are "unknown", so autopilot must still hold them for review
    assert all(d["status"] == "pending_review" for d in pw.draft(c["id"]))


def test_daily_cap_respects_warmup(pw):
    c = make_campaign(pw, daily_cap=500, mailbox_age_days=0)
    pw.discover(c["id"], 8)
    for d in pw.draft(c["id"]):
        pw.review(d["id"], approve=True)
    assert dv.daily_limit(500, 0) == 20
    assert pw.send(c["id"])["sent"] <= 20


def test_send_requires_postal_address(pw):
    c = make_campaign(pw, postal_address="")
    with pytest.raises(WorkflowError):
        pw.send(c["id"])


def test_csv_import_dedupes(pw):
    c = make_campaign(pw)
    csv_text = "company,website,contact_name,email\nFoo,https://foo.example,Jane Roe,jane@foo.example\n" \
               "Foo,https://foo.example,Jane Roe,jane@foo.example\n,,,\n"
    assert len(pw.import_csv(c["id"], csv_text)) == 1


def test_guess_and_lint():
    assert dv.guess_emails("José María Pérez", "acme.io")[0] == "jose.perez@acme.io"
    assert dv.check_email("info@acme.io", check_dns=False).status == "risky"
    assert dv.check_email("nope", check_dns=False).status == "invalid"
    assert dv.lint_copy("hi", "Act now! Click here: http://a.co http://b.co")
    assert dv.lint_copy("quick question", "Hi Sam, saw you're hiring SDRs.") == []


def test_api_smoke(tmp_path):
    app = create_app(Pipewright(DB(str(tmp_path / "api.db")), MockAgent(), FakeMailer(), check_dns=False))
    client = TestClient(app)
    assert client.get("/").status_code == 200
    c = client.post("/api/campaigns", json={"description": "Payroll software", "sender_email": "a@b.example",
                                            "postal_address": "x"}).json()
    assert client.post(f"/api/campaigns/{c['id']}/prospects/discover", json={"count": 3}).status_code == 200
    drafts = client.post(f"/api/campaigns/{c['id']}/drafts", json={"count": 3}).json()
    assert client.post(f"/api/messages/{drafts[0]['id']}/review", json={"approve": True}).status_code == 200
    assert client.post(f"/api/campaigns/{c['id']}/send").json()["sent"] == 1
    stats = client.get(f"/api/campaigns/{c['id']}/stats").json()
    assert stats["contacted"] == 1 and stats["credits_used"] > 0
    assert "company" in client.get(f"/api/campaigns/{c['id']}/export.csv").text
    assert client.post("/api/campaigns", json={}).status_code == 400
