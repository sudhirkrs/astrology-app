"""Outbound delivery through the customer's own mailbox (SMTP) or a local dry-run outbox."""

from __future__ import annotations

import json
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


class Mailer:
    """Sends via SMTP when PIPEWRIGHT_SMTP_HOST is set; otherwise appends to an outbox file.

    Dry-run is the default on purpose: nothing leaves the machine until the
    customer connects a mailbox they own.
    """

    def __init__(self):
        self.host = os.environ.get("PIPEWRIGHT_SMTP_HOST")
        self.port = int(os.environ.get("PIPEWRIGHT_SMTP_PORT", "587"))
        self.user = os.environ.get("PIPEWRIGHT_SMTP_USER")
        self.password = os.environ.get("PIPEWRIGHT_SMTP_PASSWORD")
        self.outbox = Path(os.environ.get("PIPEWRIGHT_OUTBOX", "outbox.jsonl"))

    @property
    def dry_run(self) -> bool:
        return not self.host

    def send(self, sender: str, to: str, subject: str, body: str, unsubscribe_url: str) -> None:
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        # RFC 8058 one-click unsubscribe: required by Gmail/Yahoo bulk-sender rules.
        msg["List-Unsubscribe"] = f"<{unsubscribe_url}>"
        msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
        msg.set_content(body)

        if self.dry_run:
            with self.outbox.open("a") as f:
                f.write(json.dumps({"from": sender, "to": to, "subject": subject, "body": body}) + "\n")
            return
        with smtplib.SMTP(self.host, self.port, timeout=30) as smtp:
            smtp.starttls()
            if self.user:
                smtp.login(self.user, self.password or "")
            smtp.send_message(msg)
