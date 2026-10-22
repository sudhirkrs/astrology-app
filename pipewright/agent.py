"""The AI side of Pipewright: ICP research, prospect discovery, copywriting, reply triage.

Three backends share one interface:

* ``ClaudeAgent`` calls the Claude API (web search + web fetch for research,
  structured outputs for every result the app stores).
* ``GeminiAgent`` calls the Gemini API (Google Search grounding + URL context
  for research, JSON-schema output for every result the app stores).
* ``MockAgent`` returns deterministic data so the product can be demoed and
  tested without an API key.
"""

from __future__ import annotations

import logging
import os
import re
import time
from typing import Protocol, TypeVar
from urllib.parse import urlparse

from pydantic import BaseModel

from .schemas import (
    ICP,
    EmailDraft,
    FollowUp,
    ProspectCandidate,
    ProspectList,
    ReplyAnalysis,
    ReplyIntent,
)

MODEL = os.environ.get("PIPEWRIGHT_MODEL", "claude-opus-5-5")
# Tried in order until one answers. Free-tier quotas differ per model (some have none),
# so a key that is refused on one Flash model often works on another.
GEMINI_MODELS = os.environ.get(
    "PIPEWRIGHT_GEMINI_MODEL",
    "gemini-2.5-flash,gemini-flash-latest,gemini-2.5-flash-lite,gemini-flash-lite-latest",
)

log = logging.getLogger("pipewright.agent")

T = TypeVar("T", bound=BaseModel)


class AgentError(RuntimeError):
    """The model call failed in a way worth showing to the user (quota, blocked prompt...)."""


class Agent(Protocol):
    name: str

    def build_icp(self, website: str, description: str) -> ICP: ...
    def find_prospects(self, icp: ICP, count: int, exclude: list[str]) -> list[ProspectCandidate]: ...
    def write_email(self, icp: ICP, sender: dict, prospect: dict) -> EmailDraft: ...
    def analyze_reply(self, icp: ICP, original: str, reply: str, booking_link: str) -> ReplyAnalysis: ...


RESEARCH_SYSTEM = """You are the research half of an outbound sales agent.
Use web search and web fetch to gather facts. Prefer primary sources (the company's
own site, careers page, press releases, reputable news). Never invent companies,
people or facts; if you cannot verify something, leave it out. Finish with a
concise factual research brief."""

COPY_SYSTEM = """You write cold emails that busy buyers actually answer.
Rules:
- Open with one specific, verifiable observation about the prospect. No flattery.
- Connect it to one pain point and one concrete outcome the seller delivers.
- Under 120 words, plain text, short paragraphs, no links in the first email.
- End with a low-friction question, not a demand for a 30-minute call.
- No hype words ("revolutionary", "game-changing"), no fake familiarity, no false urgency.
- Never claim results, customers or facts that are not in the brief."""

REPLY_SYSTEM = """You triage replies to cold emails for a sales team.
Classify the intent and, when a response is warranted, draft a short, human reply.
For interested prospects, propose a meeting using the booking link.
For unsubscribe or not_interested, suggested_reply must be empty: the prospect is removed, not pitched again."""


class ClaudeAgent:
    name = "claude"

    def __init__(self, client=None, model: str = MODEL):
        import anthropic

        self.client = client or anthropic.Anthropic()
        self.model = model

    # -- plumbing -----------------------------------------------------------

    def _research(self, task: str) -> str:
        """Free-form research with Anthropic's server-side web tools."""
        messages = [{"role": "user", "content": task}]
        for _ in range(6):  # server tools may pause long turns; resume a few times
            resp = self.client.beta.messages.create(
                model=self.model,
                max_tokens=16000,
                system=RESEARCH_SYSTEM,
                messages=messages,
                tools=[
                    {"type": "web_search_20260209", "name": "web_search", "max_uses": 8},
                    {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 8},
                ],
                output_config={"effort": "medium"},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
            if resp.stop_reason == "refusal":
                raise RuntimeError("Research request was declined by the model.")
            if resp.stop_reason != "pause_turn":
                return "\n".join(b.text for b in resp.content if b.type == "text")
            messages.append({"role": "assistant", "content": resp.content})
        raise RuntimeError("Research did not finish.")

    def _structured(self, system: str, prompt: str, schema: type[T], effort: str = "medium") -> T:
        resp = self.client.beta.messages.parse(
            model=self.model,
            max_tokens=16000,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            output_format=schema,
            output_config={"effort": effort},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        if resp.stop_reason == "refusal" or resp.parsed_output is None:
            raise RuntimeError(f"Model did not return a valid {schema.__name__}.")
        return resp.parsed_output

    # -- agent steps --------------------------------------------------------

    def build_icp(self, website: str, description: str) -> ICP:
        brief = self._research(
            f"Research this company so we can plan outbound sales for it.\n"
            f"Website: {website or '(none given)'}\nFounder's description: {description or '(none given)'}\n\n"
            "Work out what they sell, pricing signals, existing customers/case studies, "
            "and which companies and roles buy it."
        )
        return self._structured(
            "You turn company research into a precise ideal customer profile for outbound sales.",
            f"Research brief:\n{brief}\n\nFounder's description: {description}\n\nProduce the ICP.",
            ICP,
        )

    def find_prospects(self, icp: ICP, count: int, exclude: list[str]) -> list[ProspectCandidate]:
        brief = self._research(
            f"Find {count} real companies that match this ideal customer profile and show a buying signal now.\n"
            f"{icp.model_dump_json(indent=2)}\n\n"
            f"Skip these domains (already prospected): {', '.join(exclude) or 'none'}.\n"
            "For each company give its homepage, the concrete evidence of fit and recent signals, "
            "and a publicly listed decision maker matching the buyer titles when you can find one "
            "on the company's own site or in press coverage."
        )
        result = self._structured(
            "You convert prospect research into a clean list. Only include companies the brief actually found.",
            f"ICP buyer titles: {icp.buyer_titles}\n\nResearch brief:\n{brief}\n\nReturn up to {count} prospects.",
            ProspectList,
        )
        return result.prospects[:count]

    def write_email(self, icp: ICP, sender: dict, prospect: dict) -> EmailDraft:
        return self._structured(
            COPY_SYSTEM,
            f"Seller: {sender['name']} at {sender['company']}\n"
            f"What they sell: {icp.product_summary}\nValue props: {icp.value_props}\n"
            f"Pain points: {icp.pain_points}\n\n"
            f"Prospect: {prospect.get('contact_name') or 'unknown name'} "
            f"({prospect.get('contact_title') or 'unknown title'}) at {prospect['company']} ({prospect['website']})\n"
            f"Why they fit: {prospect.get('why_fit', '')}\nSignals: {prospect.get('signals', [])}\n\n"
            "Write the first email and two follow-ups.",
            EmailDraft,
        )

    def analyze_reply(self, icp: ICP, original: str, reply: str, booking_link: str) -> ReplyAnalysis:
        return self._structured(
            REPLY_SYSTEM,
            f"We sell: {icp.product_summary}\nBooking link: {booking_link or '(none - ask for times)'}\n\n"
            f"Our email:\n{original}\n\nTheir reply:\n{reply}",
            ReplyAnalysis,
            effort="low",
        )


class GeminiAgent(ClaudeAgent):
    """Same prompts and steps as ClaudeAgent; only the two plumbing calls differ."""

    name = "gemini"
    MAX_WAIT = 20  # seconds we will wait out a per-minute limit before trying the next model

    def __init__(self, client=None, model: str = GEMINI_MODELS):
        from google import genai
        from google.genai import types

        self.types = types
        retry = types.HttpRetryOptions(attempts=3, initial_delay=2, max_delay=10, http_status_codes=[500, 503, 504])
        self.client = client or genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
            http_options=types.HttpOptions(retry_options=retry),
        )
        self.models = [m.strip() for m in model.split(",") if m.strip()]

    @staticmethod
    def _retry_delay(err) -> float | None:
        """Seconds Google asks us to wait (RetryInfo), or None when the quota is simply exhausted or zero."""
        details = (err.details or {}).get("error", {}).get("details", []) if isinstance(err.details, dict) else []
        for d in details:
            if str(d.get("@type", "")).endswith("RetryInfo"):
                try:
                    return float(str(d.get("retryDelay", "")).rstrip("s"))
                except ValueError:
                    return None
        return None

    def _generate(self, prompt: str, config):
        from google.genai import errors

        tried = []
        for model in list(self.models):
            for attempt in (0, 1):
                try:
                    resp = self.client.models.generate_content(model=model, contents=prompt, config=config)
                except errors.APIError as e:
                    delay = self._retry_delay(e) if e.code == 429 else None
                    log.warning("gemini model=%s attempt=%d failed: %s %s (retry_delay=%s)",
                                model, attempt, e.code, e.status, delay)
                    if delay is not None and delay <= self.MAX_WAIT and attempt == 0:
                        time.sleep(delay)
                        continue
                    if e.code in (429, 404, 403):  # no quota / not available for this key: try the next model
                        tried.append(f"{model} ({e.code})")
                        break
                    raise AgentError(f"Gemini API error {e.code}: {e.message}") from e
                if model != self.models[0]:  # remember what works so later calls skip the dead models
                    self.models.remove(model)
                    self.models.insert(0, model)
                    log.warning("gemini switched to model=%s", model)
                return resp
        raise AgentError(
            "Gemini refused every model for this key (" + ", ".join(tried) + "). "
            "Check your limits at https://aistudio.google.com/rate-limit; "
            "free-tier quota may be used up for today or unavailable for these models."
        )

    def _research(self, task: str) -> str:
        t = self.types
        resp = self._generate(task, t.GenerateContentConfig(
            system_instruction=RESEARCH_SYSTEM,
            tools=[t.Tool(google_search=t.GoogleSearch()), t.Tool(url_context=t.UrlContext())],
        ))
        if not resp.text:
            raise AgentError("Gemini returned no research (the request may have been blocked).")
        return resp.text

    def _structured(self, system: str, prompt: str, schema: type[T], effort: str = "medium") -> T:
        resp = self._generate(prompt, self.types.GenerateContentConfig(
            system_instruction=system, response_mime_type="application/json", response_schema=schema,
        ))
        if isinstance(resp.parsed, schema):
            return resp.parsed
        try:
            return schema.model_validate_json(resp.text or "")
        except ValueError as e:
            raise AgentError(f"Gemini did not return a valid {schema.__name__}.") from e


# ---------------------------------------------------------------------------


def _domain(url: str) -> str:
    host = urlparse(url if "//" in url else f"https://{url}").netloc or url
    return host.lower().removeprefix("www.")


class MockAgent:
    """Deterministic stand-in used for demos and tests (no network, no API key)."""

    name = "demo"

    SAMPLE = [
        ("Northwind Analytics", "northwind-analytics.example", "Priya Raman", "VP Sales"),
        ("Brightloop Health", "brightloop.example", "Marcus Lee", "Head of Growth"),
        ("Cedar & Co Logistics", "cedarco.example", "Elena Petrova", "COO"),
        ("Quanta Payroll", "quantapayroll.example", "Tom Okafor", "Founder & CEO"),
        ("Helio Robotics", "heliorobotics.example", "Aiko Tanaka", "Director of Revenue"),
        ("Mapleleaf Dental Group", "mapleleafdental.example", "", ""),
        ("Stackwise DevTools", "stackwise.example", "Jonas Berg", "CRO"),
        ("Orbit Freight", "orbitfreight.example", "Sara Nunez", "VP Business Development"),
    ]

    def build_icp(self, website: str, description: str) -> ICP:
        what = description.strip() or f"the product at {website}"
        return ICP(
            product_summary=f"{what[:200]}",
            value_props=["Books more qualified meetings", "Cuts manual prospecting time", "Personalizes outreach at scale"],
            target_industries=["B2B SaaS", "Professional services", "Logistics"],
            company_size="20-500 employees",
            geographies=["United States", "United Kingdom", "India"],
            buyer_titles=["Founder", "VP Sales", "Head of Growth"],
            pain_points=["Pipeline depends on founder-led sales", "SDR hiring is slow and expensive"],
            buying_signals=["Hiring SDRs or AEs", "Recently raised a seed or Series A", "Launched a new product"],
            disqualifiers=["Fewer than 5 employees", "Pure B2C"],
            search_queries=["series A B2B SaaS hiring SDR", "startups hiring first sales hire"],
        )

    def find_prospects(self, icp: ICP, count: int, exclude: list[str]) -> list[ProspectCandidate]:
        out = []
        for i, (company, domain, name, title) in enumerate(self.SAMPLE):
            if domain in exclude:
                continue
            out.append(
                ProspectCandidate(
                    company=company,
                    website=f"https://{domain}",
                    why_fit=f"{company} sells to {icp.target_industries[0]} buyers and is scaling its go-to-market team.",
                    signals=["Hiring 2 SDRs (careers page)"] if i % 2 == 0 else ["Announced new product line last month"],
                    fit_score=92 - i * 6,
                    contact_name=name,
                    contact_title=title,
                )
            )
            if len(out) == count:
                break
        return out

    def write_email(self, icp: ICP, sender: dict, prospect: dict) -> EmailDraft:
        first = (prospect.get("contact_name") or "there").split()[0]
        signal = (prospect.get("signals") or ["your recent growth"])[0]
        signal = re.sub(r"\s*\(.*?\)", "", signal)
        return EmailDraft(
            subject=f"{prospect['company'].split()[0].lower()} + pipeline",
            body=(
                f"Hi {first},\n\nNoticed this about {prospect['company']}: {signal[0].lower() + signal[1:]}. "
                f"Teams at that stage usually find "
                f"{icp.pain_points[0].lower()}.\n\n{sender['company']} {icp.value_props[0].lower()} "
                f"without adding headcount.\n\nWorth a quick look, or is this not a priority right now?"
            ),
            personalization_hook=signal,
            followups=[
                FollowUp(wait_days=3, body=f"Hi {first}, one idea: we can run a free 20-lead pilot so you can judge quality first."),
                FollowUp(wait_days=7, body=f"Hi {first}, closing the loop. Should I reach out to someone else on your team instead?"),
            ],
        )

    def analyze_reply(self, icp: ICP, original: str, reply: str, booking_link: str) -> ReplyAnalysis:
        text = reply.lower()
        rules = [
            (("unsubscribe", "remove me", "stop emailing"), ReplyIntent.unsubscribe),
            (("out of office", "on leave", "vacation"), ReplyIntent.out_of_office),
            (("not interested", "no thanks", "no thank you"), ReplyIntent.not_interested),
            (("call", "meeting", "demo", "chat", "time"), ReplyIntent.meeting_request),
            (("interested", "tell me more", "sounds good"), ReplyIntent.interested),
            (("next quarter", "later", "not now"), ReplyIntent.not_now),
            (("?",), ReplyIntent.question),
        ]
        intent = next((i for keys, i in rules if any(k in text for k in keys)), ReplyIntent.question)
        suggested = ""
        if intent in (ReplyIntent.interested, ReplyIntent.meeting_request):
            suggested = f"Great to hear! Grab any slot that works here: {booking_link or '[booking link]'}"
        elif intent == ReplyIntent.question:
            suggested = "Good question. Happy to walk you through it; would a 15-minute call help?"
        elif intent == ReplyIntent.not_now:
            suggested = "Totally understand. I'll check back next quarter."
        return ReplyAnalysis(intent=intent, summary=reply[:140], suggested_reply=suggested, referral_name="")


def get_agent() -> Agent:
    """Claude if its credentials are set, else Gemini if a Gemini key is set, else the offline demo agent."""
    if os.environ.get("PIPEWRIGHT_MOCK") == "1":
        return MockAgent()
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return ClaudeAgent()
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return GeminiAgent()
    return MockAgent()
