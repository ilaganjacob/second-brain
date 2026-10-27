"""Text in, proposals out. One LLM call does both parsing and categorizing."""

import uuid
from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from pydantic import ValidationError

from api.llm import LLMProvider
from api.models import TORONTO
from api.repository import ProposalIn
from api.schemas import ApplicationEvent, Note, ParsedItem, item_adapter, llm_schema

LOCAL = ZoneInfo(TORONTO)
LOW_CONFIDENCE = 0.5


@dataclass(frozen=True)
class OpenApplication:
    id: str
    company: str
    role: str | None
    stage: str


RULES = """\
You turn a short personal log message into structured items. One message can hold several items.

Domains:
- application: a job or freelance application event (applied, screen, interview, offer, rejected, withdrawn).
  If it matches an open application below (same company, and same role when a role is given), copy that id into application_id. Otherwise application_id is null.
- meal: prepped (meal prep), ate_out (restaurant, takeout, delivery, bought lunch), home (cooked at home).
- checkin: energy, mood and sleep quality, each 1-5. Leave a score null if it isn't given. Never invent scores.
  A check-in rates the day it's logged. Sleep is last night's sleep, but it still belongs to today's check-in, so occurred_on is today unless the user names another day.
- spending: money spent, in CAD. A bought meal is BOTH a spending item and a meal item with kind ate_out.
- note: anything else, including workouts and rides (those are imported from Strava, never logged here), and anything you can't place confidently.

Rules:
- A number next to something you buy (a merchant, food, drink, a subscription, a ride-hail) is CAD spending even without a $ sign: "Netflix 18.99", "coffee 5.50".
- A number whose meaning is unclear ("14 zwift": minutes? km? dollars?) is a low-confidence note. Never guess the unit.
- Resolve relative dates ("yesterday", "monday") against today's date below. occurred_on is the local date it happened.
- confidence is 0-1. Use 0.9+ only when nothing was guessed; below 0.7 when you inferred anything important.
- Keep company and merchant names as the user wrote them, with normal capitalization.
- Never drop information: if part of the message fits no domain, put that part in a note.
- Never add a note that only repeats what another item already records ("uber home $23" is one spending item, nothing more).
"""


def build_system_prompt(now: datetime, open_applications: list[OpenApplication]) -> str:
    local = now.astimezone(LOCAL)
    lines = [RULES, f"Today is {local:%A %Y-%m-%d}, local time {local:%H:%M} (Toronto)."]
    if open_applications:
        lines.append("\nOpen applications:")
        lines += [
            f"- id={a.id} company={a.company} role={a.role or 'unknown'} stage={a.stage}"
            for a in open_applications
        ]
    else:
        lines.append("\nOpen applications: none.")
    return "\n".join(lines)


def _occurred_at(day: date, now: datetime) -> datetime:
    """Today's items keep the current time; other days get local noon."""
    local_now = now.astimezone(LOCAL)
    if day == local_now.date():
        return local_now
    return datetime.combine(day, time(12, 0), tzinfo=LOCAL)


def _resolve_application(item: ApplicationEvent, known_ids: set[str]) -> ApplicationEvent:
    confidence = item.confidence
    application_id = item.application_id
    if application_id is not None and application_id not in known_ids:
        # The model invented an id. Treat it as new, and make sure it gets a look.
        application_id = None
        confidence = min(confidence, LOW_CONFIDENCE)
    if application_id is None:
        if item.stage != "applied":
            # An update to an application we have no record of.
            confidence = min(confidence, LOW_CONFIDENCE)
        application_id = f"app_{uuid.uuid4().hex[:8]}"
    return item.model_copy(update={"application_id": application_id, "confidence": confidence})


def _to_proposal(item: ParsedItem, now: datetime) -> ProposalIn:
    payload = item.model_dump(mode="json", exclude={"domain", "occurred_on", "confidence"})
    return ProposalIn(
        domain=item.domain,
        occurred_at=_occurred_at(item.occurred_on, now),
        payload=payload,
        confidence=item.confidence,
    )


def parse(
    text: str,
    provider: LLMProvider,
    now: datetime,
    open_applications: list[OpenApplication] | None = None,
) -> list[ProposalIn]:
    """Parse one capture. LLMError propagates, so the caller can keep the raw text and retry."""
    open_applications = open_applications or []
    reply = provider.complete_json(
        system=build_system_prompt(now, open_applications),
        user=text,
        schema=llm_schema(),
        schema_name="parsed_log",
    )
    today = now.astimezone(LOCAL).date()
    known_ids = {a.id for a in open_applications}

    items: list[ParsedItem] = []
    for raw in reply.get("items", []):
        try:
            item = item_adapter.validate_python(raw)
        except ValidationError:
            # Out-of-range or malformed: keep it visible as a note instead of trusting it.
            item = Note(domain="note", occurred_on=today, confidence=0, text=f"Unreadable item: {raw}")
        if isinstance(item, ApplicationEvent):
            item = _resolve_application(item, known_ids)
        items.append(item)

    if not items:
        items = [Note(domain="note", occurred_on=today, confidence=0, text=text)]
    return [_to_proposal(item, now) for item in items]
