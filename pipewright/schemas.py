"""Structured shapes shared by the agent, the database layer and the API."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ICP(BaseModel):
    """Ideal customer profile the agent derives from the seller's website."""

    product_summary: str = Field(description="One or two sentences: what the seller sells and to whom.")
    value_props: list[str] = Field(description="Concrete outcomes the product delivers, strongest first.")
    target_industries: list[str]
    company_size: str = Field(description="Employee range, e.g. '20-200 employees'.")
    geographies: list[str]
    buyer_titles: list[str] = Field(description="Job titles of the people who buy or champion the product.")
    pain_points: list[str]
    buying_signals: list[str] = Field(description="Observable events that suggest a company needs this now (hiring, funding, launches...).")
    disqualifiers: list[str] = Field(description="Traits that make a company a bad fit.")
    search_queries: list[str] = Field(description="Web search queries that would surface matching companies.")


class ProspectCandidate(BaseModel):
    company: str
    website: str = Field(description="Company homepage URL.")
    why_fit: str = Field(description="One sentence tying the company to the ICP, citing something specific.")
    signals: list[str] = Field(description="Specific, recent evidence found on the web (hiring, funding, launches...).")
    fit_score: int = Field(description="0-100 match against the ICP.")
    contact_name: str = Field(description="Publicly listed decision maker, or empty string if none found.")
    contact_title: str = Field(description="Their title, or empty string.")


class ProspectList(BaseModel):
    prospects: list[ProspectCandidate]


class FollowUp(BaseModel):
    wait_days: int
    body: str


class EmailDraft(BaseModel):
    subject: str = Field(description="Under 8 words, lowercase-friendly, no clickbait.")
    body: str = Field(description="Plain-text email body under 120 words, no signature block.")
    personalization_hook: str = Field(description="The specific fact about the prospect the opener relies on.")
    followups: list[FollowUp] = Field(description="Two short follow-ups, each adding new value.")


class ReplyIntent(str, Enum):
    interested = "interested"
    meeting_request = "meeting_request"
    question = "question"
    not_now = "not_now"
    not_interested = "not_interested"
    unsubscribe = "unsubscribe"
    out_of_office = "out_of_office"
    wrong_person = "wrong_person"


class ReplyAnalysis(BaseModel):
    intent: ReplyIntent
    summary: str
    suggested_reply: str = Field(description="Draft response, or empty string when no reply should be sent.")
    referral_name: str = Field(description="If the prospect pointed to someone else, their name; otherwise empty string.")
