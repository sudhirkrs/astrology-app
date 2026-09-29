"""Guardrails that keep senders out of spam folders and on the right side of the law."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+'-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

ROLE_PREFIXES = {"info", "sales", "support", "admin", "contact", "hello", "office", "team", "billing", "noreply", "no-reply"}
DISPOSABLE_DOMAINS = {"mailinator.com", "guerrillamail.com", "10minutemail.com", "tempmail.com", "yopmail.com"}

SPAM_TRIGGERS = [
    "act now", "100% free", "guaranteed", "risk-free", "no obligation", "click here", "limited time",
    "winner", "cash bonus", "double your", "earn money", "urgent", "buy now", "$$$", "!!!",
]

# Conservative warm-up ramp for a fresh mailbox: sends/day by week of use.
WARMUP_RAMP = [20, 35, 50, 75, 100]


def _ascii(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def guess_emails(full_name: str, domain: str) -> list[str]:
    """Most common corporate address patterns, most likely first."""
    parts = [p for p in re.split(r"[\s\-']+", _ascii(full_name)) if p.isalpha()]
    if not parts or not domain:
        return []
    first, last = parts[0], parts[-1] if len(parts) > 1 else ""
    patterns = [f"{first}.{last}", f"{first}", f"{first[0]}{last}", f"{first}{last}", f"{first}_{last}"] if last else [first]
    seen, out = set(), []
    for p in patterns:
        addr = f"{p}@{domain}"
        if addr not in seen and EMAIL_RE.match(addr):
            seen.add(addr)
            out.append(addr)
    return out


def has_mx(domain: str) -> bool | None:
    """True/False when DNS answers, None when it can't be checked (no dnspython or no network)."""
    try:
        import dns.exception
        import dns.resolver
    except ImportError:
        return None
    try:
        return len(dns.resolver.resolve(domain, "MX", lifetime=3)) > 0
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return False
    except dns.exception.DNSException:
        return None


@dataclass
class EmailCheck:
    email: str
    status: str  # valid | risky | invalid | unknown
    reasons: list[str] = field(default_factory=list)


def check_email(email: str, check_dns: bool = True) -> EmailCheck:
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        return EmailCheck(email, "invalid", ["malformed address"])
    local, domain = email.split("@", 1)
    reasons = []
    if domain in DISPOSABLE_DOMAINS:
        return EmailCheck(email, "invalid", ["disposable domain"])
    if local in ROLE_PREFIXES:
        reasons.append("role account (lower reply rate, higher complaint risk)")
    mx = has_mx(domain) if check_dns else None
    if mx is False:
        return EmailCheck(email, "invalid", reasons + ["domain has no MX record"])
    if mx is None:
        return EmailCheck(email, "risky" if reasons else "unknown", reasons + ["MX not checked"])
    return EmailCheck(email, "risky" if reasons else "valid", reasons)


def lint_copy(subject: str, body: str) -> list[str]:
    """Human-readable warnings; empty list means the copy is clean."""
    warnings = []
    text = f"{subject}\n{body}".lower()
    hits = [t for t in SPAM_TRIGGERS if t in text]
    if hits:
        warnings.append(f"spam-trigger phrases: {', '.join(hits)}")
    words = len(body.split())
    if words > 150:
        warnings.append(f"body is {words} words; aim for under 120")
    if len(re.findall(r"https?://", body)) > 1:
        warnings.append("more than one link hurts first-touch deliverability")
    if subject.isupper() and len(subject) > 3:
        warnings.append("all-caps subject line")
    if "{{" in text or "[first name]" in text:
        warnings.append("unfilled template placeholder")
    return warnings


def daily_limit(configured_cap: int, mailbox_age_days: int) -> int:
    """Never exceed the warm-up ramp, whatever the user configured."""
    week = min(mailbox_age_days // 7, len(WARMUP_RAMP) - 1)
    return max(0, min(configured_cap, WARMUP_RAMP[week]))


def compliance_footer(company: str, postal_address: str, unsubscribe_url: str) -> str:
    """CAN-SPAM / GDPR-friendly footer: who we are, where we are, how to opt out."""
    return (
        f"\n\n--\n{company} · {postal_address or 'postal address required before sending'}\n"
        f"Not relevant? Reply 'unsubscribe' or opt out here: {unsubscribe_url}"
    )
