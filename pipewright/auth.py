"""Sign-in via Supabase Auth.

The browser signs in with supabase-js (magic link) and sends the access token
as a Bearer header. We confirm it with Supabase's /auth/v1/user endpoint and
cache the answer briefly. When SUPABASE_URL is not configured (local dev),
auth is off and everything belongs to the "local" owner.

PIPEWRIGHT_ALLOWED_EMAILS keeps a public deployment private: a comma-separated
list of addresses and/or "@domain.com" entries. Anyone else who signs in is
refused, so strangers can't spend your Claude credits or send mail.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from fastapi import Header, HTTPException

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
_cache: dict[str, tuple[float, dict]] = {}
TTL = 300


def enabled() -> bool:
    return bool(SUPABASE_URL and SUPABASE_ANON_KEY)


def allowed(email: str) -> bool:
    rules = [r.strip().lower() for r in os.environ.get("PIPEWRIGHT_ALLOWED_EMAILS", "").split(",") if r.strip()]
    if not rules:
        return True
    email = (email or "").lower()
    return any(email == r or (r.startswith("@") and email.endswith(r)) for r in rules)


def _lookup(token: str) -> dict | None:
    hit = _cache.get(token)
    if hit and hit[0] > time.time():
        return hit[1]
    req = urllib.request.Request(f"{SUPABASE_URL}/auth/v1/user",
                                 headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            user = json.load(r)
    except urllib.error.HTTPError:
        return None
    except OSError as e:
        raise HTTPException(503, "auth service unreachable") from e
    _cache[token] = (time.time() + TTL, user)
    if len(_cache) > 1000:
        _cache.clear()
    return user


def current_user(authorization: str | None = Header(default=None)) -> dict:
    if not enabled():
        return {"id": "local", "email": "local"}
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "sign in required")
    user = _lookup(authorization.split(" ", 1)[1].strip())
    if not user or not user.get("id"):
        raise HTTPException(401, "session expired, sign in again")
    if not allowed(user.get("email", "")):
        raise HTTPException(403, f"{user.get('email')} is not on this workspace's allow-list")
    return {"id": user["id"], "email": user.get("email", "")}
