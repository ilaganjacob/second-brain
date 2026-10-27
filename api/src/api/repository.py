"""The only way the app writes data.

There's deliberately no function that updates or deletes an entry. A fix is a new
entry that supersedes the old one, and a delete is a tombstone entry. The
database triggers in db.py back this up.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import exists
from sqlalchemy.orm import aliased
from sqlmodel import Session, select

from api.models import Capture, CaptureSource, Entry, Proposal, utcnow


class InvalidState(Exception):
    """The action doesn't make sense for the row's current state."""


class NotFound(Exception):
    pass


@dataclass
class ProposalIn:
    domain: str
    occurred_at: datetime
    payload: dict[str, Any]
    confidence: float = 1.0


def add_capture(
    session: Session,
    raw_text: str | None,
    source: CaptureSource = "chat",
    file_hash: str | None = None,
) -> Capture:
    capture = Capture(raw_text=raw_text, source=source, file_hash=file_hash)
    session.add(capture)
    session.commit()
    session.refresh(capture)
    return capture


def add_proposals(session: Session, capture_id: int, items: list[ProposalIn]) -> list[Proposal]:
    proposals = [
        Proposal(
            capture_id=capture_id,
            domain=item.domain,
            occurred_at=item.occurred_at,
            payload=item.payload,
            confidence=item.confidence,
        )
        for item in items
    ]
    session.add_all(proposals)
    session.commit()
    for proposal in proposals:
        session.refresh(proposal)
    return proposals


def _pending_proposal(session: Session, proposal_id: int) -> Proposal:
    proposal = session.get(Proposal, proposal_id)
    if proposal is None:
        raise NotFound(f"proposal {proposal_id}")
    if proposal.status != "pending":
        raise InvalidState(f"proposal {proposal_id} is already {proposal.status}")
    return proposal


def approve_proposal(
    session: Session,
    proposal_id: int,
    payload: dict[str, Any] | None = None,
    occurred_at: datetime | None = None,
) -> Entry:
    """Turn a pending proposal into an entry. Pass payload/occurred_at to approve an edit."""
    proposal = _pending_proposal(session, proposal_id)
    entry = Entry(
        capture_id=proposal.capture_id,
        proposal_id=proposal.id,
        domain=proposal.domain,
        occurred_at=occurred_at or proposal.occurred_at,
        payload=payload if payload is not None else proposal.payload,
    )
    proposal.status = "approved"
    proposal.decided_at = utcnow()
    session.add_all([entry, proposal])
    session.commit()
    session.refresh(entry)
    return entry


def reject_proposal(session: Session, proposal_id: int) -> Proposal:
    proposal = _pending_proposal(session, proposal_id)
    proposal.status = "rejected"
    proposal.decided_at = utcnow()
    session.add(proposal)
    session.commit()
    session.refresh(proposal)
    return proposal


def _current_entry(session: Session, entry_id: int) -> Entry:
    entry = session.get(Entry, entry_id)
    if entry is None:
        raise NotFound(f"entry {entry_id}")
    if entry.kind != "fact":
        raise InvalidState(f"entry {entry_id} is a {entry.kind}")
    replaced = session.exec(select(Entry.id).where(Entry.supersedes_id == entry_id)).first()
    if replaced is not None:
        raise InvalidState(f"entry {entry_id} was already replaced by entry {replaced}")
    return entry


def supersede_entry(
    session: Session,
    entry_id: int,
    payload: dict[str, Any],
    occurred_at: datetime | None = None,
) -> Entry:
    """Correct an entry by adding a new one. The original row is never touched."""
    old = _current_entry(session, entry_id)
    new = Entry(
        capture_id=old.capture_id,
        proposal_id=old.proposal_id,
        domain=old.domain,
        occurred_at=occurred_at or old.occurred_at,
        tz=old.tz,
        payload=payload,
        supersedes_id=old.id,
        is_private=old.is_private,
    )
    session.add(new)
    session.commit()
    session.refresh(new)
    return new


def tombstone_entry(session: Session, entry_id: int) -> Entry:
    """Delete an entry by adding a tombstone that supersedes it."""
    old = _current_entry(session, entry_id)
    tombstone = Entry(
        capture_id=old.capture_id,
        kind="tombstone",
        domain=old.domain,
        occurred_at=old.occurred_at,
        tz=old.tz,
        payload={},
        supersedes_id=old.id,
    )
    session.add(tombstone)
    session.commit()
    session.refresh(tombstone)
    return tombstone


def current_entries(session: Session, domain: str | None = None) -> list[Entry]:
    """Facts that nothing has replaced or deleted: what the dashboard counts."""
    newer = aliased(Entry)
    replaced = exists().where(newer.supersedes_id == Entry.id)
    query = select(Entry).where(Entry.kind == "fact", ~replaced)
    if domain is not None:
        query = query.where(Entry.domain == domain)
    return list(session.exec(query.order_by(Entry.occurred_at)))
