from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from api import repository as repo
from api.models import Entry, Goal, Proposal

TORONTO = ZoneInfo("America/Toronto")


def capture_with_proposal(session, payload=None, occurred_at=None):
    capture = repo.add_capture(session, "$14 lunch")
    [proposal] = repo.add_proposals(
        session,
        capture.id,
        [
            repo.ProposalIn(
                domain="spending",
                occurred_at=occurred_at or datetime(2026, 10, 26, 16, 0, tzinfo=UTC),
                payload=payload or {"amount": 14.0, "category": "food"},
                confidence=0.9,
            )
        ],
    )
    return capture, proposal


def test_approving_a_proposal_creates_one_linked_entry(session):
    capture, proposal = capture_with_proposal(session)

    entry = repo.approve_proposal(session, proposal.id)

    assert session.exec(select(Entry)).all() == [entry]
    assert entry.capture_id == capture.id
    assert entry.proposal_id == proposal.id
    assert entry.payload == {"amount": 14.0, "category": "food"}
    assert session.get(Proposal, proposal.id).status == "approved"


def test_approving_with_an_edit_uses_the_edited_payload(session):
    _, proposal = capture_with_proposal(session)

    entry = repo.approve_proposal(session, proposal.id, payload={"amount": 41.0, "category": "food"})

    assert entry.payload["amount"] == 41.0
    # The proposal keeps what the model said, so misparses stay visible.
    assert session.get(Proposal, proposal.id).payload["amount"] == 14.0


def test_a_proposal_can_only_be_decided_once(session):
    _, proposal = capture_with_proposal(session)
    repo.reject_proposal(session, proposal.id)

    with pytest.raises(repo.InvalidState):
        repo.approve_proposal(session, proposal.id)
    assert session.exec(select(Entry)).all() == []


def test_superseding_leaves_the_original_unchanged(session):
    _, proposal = capture_with_proposal(session)
    original = repo.approve_proposal(session, proposal.id)

    fixed = repo.supersede_entry(session, original.id, {"amount": 14.5, "category": "food"})

    session.expire_all()
    assert session.get(Entry, original.id).payload == {"amount": 14.0, "category": "food"}
    assert fixed.supersedes_id == original.id
    assert repo.current_entries(session) == [fixed]


def test_an_entry_can_only_be_superseded_once(session):
    _, proposal = capture_with_proposal(session)
    original = repo.approve_proposal(session, proposal.id)
    repo.supersede_entry(session, original.id, {"amount": 15.0})

    with pytest.raises(repo.InvalidState):
        repo.supersede_entry(session, original.id, {"amount": 16.0})


def test_a_tombstone_hides_the_entry(session):
    _, proposal = capture_with_proposal(session)
    entry = repo.approve_proposal(session, proposal.id)

    repo.tombstone_entry(session, entry.id)

    assert repo.current_entries(session) == []
    assert session.get(Entry, entry.id) is not None


def test_current_entries_filters_by_domain(session):
    _, proposal = capture_with_proposal(session)
    repo.approve_proposal(session, proposal.id)

    assert len(repo.current_entries(session, "spending")) == 1
    assert repo.current_entries(session, "application") == []


@pytest.mark.parametrize("statement", ["UPDATE entries SET domain = 'x'", "DELETE FROM entries"])
def test_the_database_refuses_edits_to_entries(engine, session, statement):
    _, proposal = capture_with_proposal(session)
    repo.approve_proposal(session, proposal.id)

    with pytest.raises(IntegrityError, match="append-only"), engine.begin() as conn:
        conn.execute(text(statement))


def test_toronto_evening_round_trips_across_midnight_utc(session):
    # 23:30 in Toronto on Oct 26 is 03:30 UTC on Oct 27.
    evening = datetime(2026, 10, 26, 23, 30, tzinfo=TORONTO)
    _, proposal = capture_with_proposal(session, occurred_at=evening)
    entry = repo.approve_proposal(session, proposal.id)

    session.expire_all()
    stored = session.get(Entry, entry.id)
    assert stored.occurred_at == evening
    assert stored.occurred_at.tzinfo is not None
    assert stored.occurred_at.astimezone(TORONTO).date().isoformat() == "2026-10-26"
    assert stored.tz == "America/Toronto"


def test_naive_datetimes_are_rejected(session):
    with pytest.raises(Exception, match="timezone-aware"):
        capture_with_proposal(session, occurred_at=datetime(2026, 10, 26, 12, 0))


def test_goals_are_seeded_once(engine):
    from api.db import init_db

    init_db(engine)
    with Session(engine) as session:
        goals = {(g.domain, g.target, g.period) for g in session.exec(select(Goal))}
    assert goals == {
        ("application", 10, "week"),
        ("spending", 1000, "month"),
        ("workout", 8, "week"),
    }
