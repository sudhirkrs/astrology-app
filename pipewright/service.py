"""Campaign workflow: ICP -> prospects -> drafts -> human approval -> send -> replies."""

from __future__ import annotations

import csv
import hashlib
import hmac
import io
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

from . import deliverability as dv
from .agent import Agent
from .db import DB
from .mailer import Mailer
from .schemas import ICP, ReplyIntent

# Published, flat credit prices: the customer always knows what an action costs.
CREDITS = {"icp": 5, "prospect": 2, "email_lookup": 1, "draft": 2, "reply_triage": 1}

SECRET = os.environ.get("PIPEWRIGHT_SECRET", "dev-secret-change-me").encode()
BASE_URL = os.environ.get("PIPEWRIGHT_BASE_URL", "http://localhost:8000")

REPLY_STATUS = {
    ReplyIntent.interested: "interested",
    ReplyIntent.meeting_request: "interested",
    ReplyIntent.question: "replied",
    ReplyIntent.not_now: "nurture",
    ReplyIntent.not_interested: "closed",
    ReplyIntent.unsubscribe: "unsubscribed",
    ReplyIntent.wrong_person: "closed",
    ReplyIntent.out_of_office: "contacted",
}


class WorkflowError(ValueError):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def unsubscribe_token(email: str) -> str:
    sig = hmac.new(SECRET, email.lower().encode(), hashlib.sha256).hexdigest()[:24]
    return f"{email.lower().encode().hex()}.{sig}"


def email_from_token(token: str) -> str | None:
    try:
        hex_email, sig = token.split(".", 1)
        email = bytes.fromhex(hex_email).decode()
    except ValueError:
        return None
    return email if hmac.compare_digest(unsubscribe_token(email), token) else None


class Pipewright:
    def __init__(self, db: DB, agent: Agent, mailer: Mailer | None = None, check_dns: bool = True):
        self.db, self.agent, self.mailer, self.check_dns = db, agent, mailer or Mailer(), check_dns

    # -- campaigns ------------------------------------------------------------

    def campaign(self, cid: int) -> dict:
        c = self.db.get("campaigns", cid)
        if not c:
            raise WorkflowError(f"campaign {cid} not found")
        return c

    def campaigns(self, owner_id: str) -> list[dict]:
        return self.db.all("SELECT id, name, website, status, created_at FROM campaigns WHERE owner_id = ? "
                           "ORDER BY id DESC", (owner_id,))

    def owns(self, owner_id: str, *, campaign_id: int | None = None, prospect_id: int | None = None,
             message_id: int | None = None) -> bool:
        if message_id is not None:
            campaign_id = self.db.one("SELECT campaign_id FROM messages WHERE id = ?", (message_id,))
        elif prospect_id is not None:
            campaign_id = self.db.one("SELECT campaign_id FROM prospects WHERE id = ?", (prospect_id,))
        if campaign_id is None:
            return False
        return self.db.one("SELECT owner_id FROM campaigns WHERE id = ?", (campaign_id,)) == owner_id

    def create_campaign(self, data: dict, owner_id: str = "local") -> dict:
        if not (data.get("website") or data.get("description")):
            raise WorkflowError("give a website or a description of what you sell")
        icp = self.agent.build_icp(data.get("website", ""), data.get("description", ""))
        allowed = {
            "name", "website", "description", "sender_name", "sender_email", "sender_company", "postal_address",
            "booking_link", "crm_webhook", "daily_cap", "mailbox_age_days", "autopilot", "autopilot_min_score",
        }
        values = {k: v for k, v in data.items() if k in allowed and v is not None}
        values.setdefault("name", data.get("sender_company") or data.get("website") or "New campaign")
        cid = self.db.insert("campaigns", {**values, "owner_id": owner_id, "icp": icp.model_dump(), "status": "active"})
        self.db.charge(cid, "icp", CREDITS["icp"])
        return self.campaign(cid)

    def update_campaign(self, cid: int, data: dict) -> dict:
        self.campaign(cid)
        if "icp" in data:
            data["icp"] = ICP.model_validate(data["icp"]).model_dump()
        allowed = {"name", "sender_name", "sender_email", "sender_company", "postal_address", "booking_link",
                   "crm_webhook", "daily_cap", "mailbox_age_days", "autopilot", "autopilot_min_score", "icp", "status"}
        self.db.update("campaigns", cid, {k: v for k, v in data.items() if k in allowed})
        return self.campaign(cid)

    # -- prospects ------------------------------------------------------------

    def _add_prospect(self, cid: int, p: dict, source: str) -> int | None:
        domain = dv._ascii(p.get("website", "")).split("//")[-1].split("/")[0].removeprefix("www.")
        email = (p.get("email") or "").strip().lower()
        if not email and p.get("contact_name") and domain:
            guesses = dv.guess_emails(p["contact_name"], domain)
            email = guesses[0] if guesses else ""
            if email:
                self.db.charge(cid, "email_lookup", CREDITS["email_lookup"], email)
        status = dv.check_email(email, self.check_dns).status if email else "missing"
        if email and self.db.is_suppressed(email):
            status = "suppressed"
        signals = p.get("signals") or []
        if isinstance(signals, str):  # CSV import: "a; b; c"
            signals = [x.strip() for x in signals.split(";") if x.strip()]
        return self.db.insert("prospects", {
                "campaign_id": cid, "company": p.get("company", domain), "website": p.get("website", ""),
                "domain": domain, "contact_name": p.get("contact_name", ""), "contact_title": p.get("contact_title", ""),
                "email": email, "email_status": status, "why_fit": p.get("why_fit", ""),
                "signals": signals, "fit_score": int(p.get("fit_score") or 0), "source": source,
        }, ignore_conflict=True)  # duplicate (campaign, domain, email) -> None

    def discover(self, cid: int, count: int = 10) -> list[dict]:
        c = self.campaign(cid)
        exclude = [r["domain"] for r in self.db.all("SELECT domain FROM prospects WHERE campaign_id = ?", (cid,))]
        found = self.agent.find_prospects(ICP.model_validate(c["icp"]), max(1, min(count, 50)), exclude)
        ids = [pid for p in found if (pid := self._add_prospect(cid, p.model_dump(), "ai_research"))]
        self.db.charge(cid, "prospect", CREDITS["prospect"] * len(ids))
        return [self.db.get("prospects", i) for i in ids]

    def import_csv(self, cid: int, text: str) -> list[dict]:
        self.campaign(cid)
        rows = csv.DictReader(io.StringIO(text.strip()))
        ids = []
        for r in rows:
            r = {k.strip().lower(): (v or "").strip() for k, v in r.items() if k}
            if not (r.get("website") or r.get("email")):
                continue
            if not r.get("website") and r.get("email"):
                r["website"] = "https://" + r["email"].split("@")[-1]
            if pid := self._add_prospect(cid, r, "csv_import"):
                ids.append(pid)
        return [self.db.get("prospects", i) for i in ids]

    def prospects(self, cid: int) -> list[dict]:
        return self.db.all("SELECT * FROM prospects WHERE campaign_id = ? ORDER BY fit_score DESC, id", (cid,))

    def set_prospect_email(self, pid: int, email: str) -> dict:
        check = dv.check_email(email, self.check_dns)
        self.db.update("prospects", pid, {"email": check.email, "email_status": check.status})
        return self.db.get("prospects", pid)

    # -- drafting & review ------------------------------------------------------

    def draft(self, cid: int, limit: int = 25) -> list[dict]:
        c = self.campaign(cid)
        icp = ICP.model_validate(c["icp"])
        sender = {"name": c["sender_name"] or "", "company": c["sender_company"] or c["name"]}
        todo = self.db.all(
            "SELECT * FROM prospects WHERE campaign_id = ? AND status = 'new' "
            "AND email_status IN ('valid', 'unknown', 'risky') ORDER BY fit_score DESC LIMIT ?",
            (cid, limit),
        )
        created = []
        for p in todo:
            d = self.agent.write_email(icp, sender, p)
            warnings = dv.lint_copy(d.subject, d.body)
            auto = bool(c["autopilot"]) and not warnings and p["fit_score"] >= c["autopilot_min_score"] \
                and p["email_status"] == "valid"
            status = "approved" if auto else "pending_review"
            mid = self.db.insert("messages", {
                "campaign_id": cid, "prospect_id": p["id"], "kind": "initial", "step": 0,
                "subject": d.subject, "body": d.body, "hook": d.personalization_hook,
                "warnings": warnings, "status": status,
            })
            for i, f in enumerate(d.followups, start=1):
                self.db.insert("messages", {
                    "campaign_id": cid, "prospect_id": p["id"], "kind": "followup", "step": i,
                    "wait_days": f.wait_days, "subject": f"Re: {d.subject}", "body": f.body,
                    "warnings": dv.lint_copy("", f.body), "status": status,
                })
            self.db.update("prospects", p["id"], {"status": "drafted"})
            self.db.charge(cid, "draft", CREDITS["draft"])
            created.append(self.db.get("messages", mid))
        return created

    def queue(self, cid: int, status: str | None = None) -> list[dict]:
        sql = ("SELECT m.*, p.company, p.contact_name, p.contact_title, p.email, p.fit_score, p.why_fit "
               "FROM messages m JOIN prospects p ON p.id = m.prospect_id WHERE m.campaign_id = ?")
        params: tuple = (cid,)
        if status:
            sql += " AND m.status = ?"
            params += (status,)
        return self.db.all(sql + " ORDER BY p.fit_score DESC, m.prospect_id, m.step", params)

    def edit_message(self, mid: int, subject: str | None, body: str | None) -> dict:
        m = self.db.get("messages", mid)
        if not m or m["status"] == "sent":
            raise WorkflowError("message not found or already sent")
        subject = subject if subject is not None else m["subject"]
        body = body if body is not None else m["body"]
        self.db.update("messages", mid, {"subject": subject, "body": body,
                                         "warnings": dv.lint_copy(subject if m["kind"] != "followup" else "", body)})
        return self.db.get("messages", mid)

    def review(self, mid: int, approve: bool, whole_sequence: bool = True) -> list[dict]:
        m = self.db.get("messages", mid)
        if not m or m["status"] == "sent":
            raise WorkflowError("message not found or already sent")
        new = "approved" if approve else "rejected"
        targets = [m]
        if whole_sequence and m["kind"] == "initial":
            targets = self.db.all("SELECT * FROM messages WHERE prospect_id = ? AND kind != 'reply' AND status != 'sent'",
                                  (m["prospect_id"],))
        for t in targets:
            self.db.update("messages", t["id"], {"status": new})
        if not approve and m["kind"] == "initial":
            self.db.update("prospects", m["prospect_id"], {"status": "skipped"})
        return [self.db.get("messages", t["id"]) for t in targets]

    # -- sending ----------------------------------------------------------------

    def sent_today(self, cid: int, now: datetime) -> int:
        return self.db.one("SELECT COUNT(*) FROM messages WHERE campaign_id = ? AND status = 'sent' "
                           "AND sent_at >= ?", (cid, _ts(now.replace(hour=0, minute=0, second=0, microsecond=0)))) or 0

    def due_messages(self, cid: int, now: datetime) -> list[dict]:
        due = []
        for m in self.queue(cid, "approved"):
            p = self.db.get("prospects", m["prospect_id"])
            if not p["email"] or self.db.is_suppressed(p["email"]):
                continue
            if m["kind"] == "reply":
                due.append(m)
            elif m["kind"] == "initial" and p["status"] in ("new", "drafted"):
                due.append(m)
            elif m["kind"] == "followup" and p["status"] == "contacted":
                prev = self.db.all("SELECT * FROM messages WHERE prospect_id = ? AND kind != 'reply' AND step = ?",
                                   (p["id"], m["step"] - 1))
                if prev and prev[0]["status"] == "sent":
                    sent_at = datetime.strptime(prev[0]["sent_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    if now - sent_at >= timedelta(days=m["wait_days"]):
                        due.append(m)
        # replies to warm leads first, then new first touches, then follow-ups
        order = {"reply": 0, "initial": 1, "followup": 2}
        return sorted(due, key=lambda m: (order[m["kind"]], -m["fit_score"]))

    def send(self, cid: int, now: datetime | None = None) -> dict:
        now = now or _now()
        c = self.campaign(cid)
        if not c["sender_email"]:
            raise WorkflowError("set a sender email before sending")
        if not c["postal_address"]:
            raise WorkflowError("a physical postal address is required in the footer (CAN-SPAM)")
        budget = dv.daily_limit(c["daily_cap"], c["mailbox_age_days"]) - self.sent_today(cid, now)
        sent = []
        for m in self.due_messages(cid, now)[: max(budget, 0)]:
            p = self.db.get("prospects", m["prospect_id"])
            unsub = f"{BASE_URL}/u/{unsubscribe_token(p['email'])}"
            body = m["body"]
            if m["kind"] != "reply":
                body += dv.compliance_footer(c["sender_company"] or c["name"], c["postal_address"], unsub)
            sender = f"{c['sender_name']} <{c['sender_email']}>" if c["sender_name"] else c["sender_email"]
            self.mailer.send(sender, p["email"], m["subject"], body, unsub)
            self.db.update("messages", m["id"], {"status": "sent", "sent_at": _ts(now),
                                                 "sent_via": "dry_run" if self.mailer.dry_run else "smtp"})
            if m["kind"] != "reply":
                self.db.update("prospects", p["id"], {"status": "contacted"})
            sent.append(m["id"])
        return {"sent": len(sent), "message_ids": sent, "remaining_today": max(budget - len(sent), 0),
                "dry_run": self.mailer.dry_run}

    def send_all_due(self, now: datetime | None = None) -> list[dict]:
        """Daily scheduler entry point: send what's due for every active, send-ready campaign."""
        results = []
        for c in self.db.all("SELECT id FROM campaigns WHERE status = 'active' AND sender_email IS NOT NULL "
                             "AND sender_email != '' AND postal_address IS NOT NULL AND postal_address != ''"):
            try:
                results.append({"campaign_id": c["id"], **self.send(c["id"], now)})
            except WorkflowError as e:
                results.append({"campaign_id": c["id"], "error": str(e)})
        return results

    # -- replies ----------------------------------------------------------------

    def record_reply(self, cid: int, from_email: str, text: str) -> dict:
        c = self.campaign(cid)
        p = next(iter(self.db.all("SELECT * FROM prospects WHERE campaign_id = ? AND email = ?",
                                  (cid, from_email.strip().lower()))), None)
        if not p:
            raise WorkflowError(f"no prospect with email {from_email} in this campaign")
        last = next(iter(self.db.all("SELECT * FROM messages WHERE prospect_id = ? AND status = 'sent' "
                                     "ORDER BY sent_at DESC, id DESC LIMIT 1", (p["id"],))), None)
        a = self.agent.analyze_reply(ICP.model_validate(c["icp"]), last["body"] if last else "", text, c["booking_link"] or "")
        self.db.charge(cid, "reply_triage", CREDITS["reply_triage"])
        self.db.insert("replies", {"prospect_id": p["id"], "body": text, "intent": a.intent.value, "summary": a.summary})
        self.db.update("prospects", p["id"], {"status": REPLY_STATUS[a.intent]})

        if a.intent != ReplyIntent.out_of_office:  # any real reply stops the automated sequence
            self.db.execute("UPDATE messages SET status = 'skipped' WHERE prospect_id = ? AND kind = 'followup' "
                             "AND status IN ('pending_review', 'approved')", (p["id"],))
        if a.intent in (ReplyIntent.unsubscribe, ReplyIntent.not_interested):
            self.db.suppress(p["email"], a.intent.value)

        reply_id = None
        if a.suggested_reply and a.intent not in (ReplyIntent.unsubscribe, ReplyIntent.not_interested):
            subject = last["subject"] if last else "Re:"
            reply_id = self.db.insert("messages", {
                "campaign_id": cid, "prospect_id": p["id"], "kind": "reply", "step": 99,
                "subject": subject if subject.lower().startswith("re:") else f"Re: {subject}",
                "body": a.suggested_reply, "warnings": [], "status": "pending_review",  # replies always need a human
            })
        if a.intent in (ReplyIntent.interested, ReplyIntent.meeting_request) and c["crm_webhook"]:
            self._webhook(c["crm_webhook"], {"event": "lead.interested", "campaign": c["name"],
                                             "prospect": self.db.get("prospects", p["id"]), "reply": text})
        return {"analysis": a.model_dump(), "prospect": self.db.get("prospects", p["id"]),
                "draft_reply": self.db.get("messages", reply_id) if reply_id else None}

    @staticmethod
    def _webhook(url: str, payload: dict) -> None:
        req = urllib.request.Request(url, json.dumps(payload, default=str).encode(),
                                     {"Content-Type": "application/json"}, method="POST")
        try:
            urllib.request.urlopen(req, timeout=5).close()
        except OSError:
            pass  # CRM sync is best-effort; the lead stays visible in the app

    def unsubscribe(self, token: str) -> str | None:
        email = email_from_token(token)
        if email:
            self.db.suppress(email, "unsubscribe_link")
            self.db.execute("UPDATE prospects SET status = 'unsubscribed' WHERE email = ?", (email,))
            self.db.execute("UPDATE messages SET status = 'skipped' WHERE status IN ('pending_review', 'approved') "
                            "AND prospect_id IN (SELECT id FROM prospects WHERE email = ?)", (email,))
        return email

    # -- reporting --------------------------------------------------------------

    def stats(self, cid: int) -> dict:
        by_status = self.db.pairs("SELECT status, COUNT(*) AS n FROM prospects WHERE campaign_id = ? GROUP BY status", (cid,))
        msgs = self.db.pairs("SELECT status, COUNT(*) AS n FROM messages WHERE campaign_id = ? GROUP BY status", (cid,))
        contacted = sum(by_status.get(s, 0) for s in ("contacted", "replied", "interested", "nurture", "closed", "unsubscribed"))
        replied = sum(by_status.get(s, 0) for s in ("replied", "interested", "nurture", "closed", "unsubscribed"))
        credits = int(self.db.one("SELECT COALESCE(SUM(credits), 0) AS c FROM ledger WHERE campaign_id = ?", (cid,)))
        return {
            "prospects": sum(by_status.values()), "prospects_by_status": by_status, "messages_by_status": msgs,
            "contacted": contacted, "replied": replied, "interested": by_status.get("interested", 0),
            "reply_rate": round(replied / contacted, 3) if contacted else 0.0,
            "credits_used": credits,
            "credits_per_interested_lead": round(credits / by_status["interested"], 1) if by_status.get("interested") else None,
        }

    def ledger(self, cid: int) -> list[dict]:
        return self.db.all("SELECT action, SUM(credits) AS credits, COUNT(*) AS events FROM ledger "
                           "WHERE campaign_id = ? GROUP BY action ORDER BY credits DESC", (cid,))

    def export_csv(self, cid: int) -> str:
        out = io.StringIO()
        cols = ["company", "website", "contact_name", "contact_title", "email", "email_status", "fit_score",
                "status", "why_fit", "signals"]
        w = csv.DictWriter(out, cols, extrasaction="ignore")
        w.writeheader()
        for p in self.prospects(cid):
            w.writerow({**p, "signals": "; ".join(p["signals"] or [])})
        return out.getvalue()
