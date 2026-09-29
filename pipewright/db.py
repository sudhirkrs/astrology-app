"""SQLite persistence. One file, no ORM: the schema is small and explicit."""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    website TEXT, description TEXT,
    sender_name TEXT, sender_email TEXT, sender_company TEXT, postal_address TEXT,
    booking_link TEXT, crm_webhook TEXT,
    daily_cap INTEGER DEFAULT 30, mailbox_age_days INTEGER DEFAULT 0,
    autopilot INTEGER DEFAULT 0, autopilot_min_score INTEGER DEFAULT 85,
    icp TEXT, status TEXT DEFAULT 'draft',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS prospects (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id),
    company TEXT, website TEXT, domain TEXT,
    contact_name TEXT, contact_title TEXT, email TEXT, email_status TEXT,
    why_fit TEXT, signals TEXT, fit_score INTEGER, source TEXT,
    status TEXT DEFAULT 'new',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (campaign_id, domain, email)
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id),
    prospect_id INTEGER NOT NULL REFERENCES prospects(id),
    kind TEXT DEFAULT 'initial',          -- initial | followup | reply
    step INTEGER DEFAULT 0, wait_days INTEGER DEFAULT 0,
    subject TEXT, body TEXT, hook TEXT, warnings TEXT,
    status TEXT DEFAULT 'pending_review', -- pending_review | approved | rejected | sent | skipped
    sent_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS replies (
    id INTEGER PRIMARY KEY,
    prospect_id INTEGER NOT NULL REFERENCES prospects(id),
    body TEXT, intent TEXT, summary TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS suppression (
    email TEXT PRIMARY KEY, reason TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ledger (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER, action TEXT, credits INTEGER, note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

JSON_COLUMNS = {"icp", "signals", "warnings"}


class DB:
    def __init__(self, path: str | None = None):
        self.path = path or os.environ.get("PIPEWRIGHT_DB", "pipewright.db")
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)

    @contextmanager
    def tx(self):
        with self._lock:
            try:
                yield self.conn
                self.conn.commit()
            except Exception:
                self.conn.rollback()
                raise

    @staticmethod
    def _encode(values: dict) -> dict:
        return {k: json.dumps(v) if k in JSON_COLUMNS and v is not None else v for k, v in values.items()}

    @staticmethod
    def row(r: sqlite3.Row | None) -> dict | None:
        if r is None:
            return None
        d = dict(r)
        for k in JSON_COLUMNS & d.keys():
            if d[k] is not None:
                d[k] = json.loads(d[k])
        return d

    def insert(self, table: str, values: dict) -> int:
        values = self._encode(values)
        cols = ", ".join(values)
        marks = ", ".join("?" for _ in values)
        with self.tx() as c:
            return c.execute(f"INSERT INTO {table} ({cols}) VALUES ({marks})", list(values.values())).lastrowid

    def update(self, table: str, row_id: int, values: dict) -> None:
        if not values:
            return
        values = self._encode(values)
        sets = ", ".join(f"{k} = ?" for k in values)
        with self.tx() as c:
            c.execute(f"UPDATE {table} SET {sets} WHERE id = ?", [*values.values(), row_id])

    def get(self, table: str, row_id: int) -> dict | None:
        return self.row(self.conn.execute(f"SELECT * FROM {table} WHERE id = ?", (row_id,)).fetchone())

    def all(self, sql: str, params: tuple = ()) -> list[dict]:
        return [self.row(r) for r in self.conn.execute(sql, params).fetchall()]

    def one(self, sql: str, params: tuple = ()):
        r = self.conn.execute(sql, params).fetchone()
        return r[0] if r else None

    # -- domain helpers -----------------------------------------------------

    def is_suppressed(self, email: str) -> bool:
        return bool(self.one("SELECT 1 FROM suppression WHERE email = ?", (email.lower(),)))

    def suppress(self, email: str, reason: str) -> None:
        with self.tx() as c:
            c.execute("INSERT OR IGNORE INTO suppression (email, reason) VALUES (?, ?)", (email.lower(), reason))

    def charge(self, campaign_id: int | None, action: str, credits: int, note: str = "") -> None:
        self.insert("ledger", {"campaign_id": campaign_id, "action": action, "credits": credits, "note": note})
