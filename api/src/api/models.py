"""Tables for v0.1. See docs/SPEC.md, "Data model".

captures and entries are append-only facts. proposals are inbox workflow state:
they change status, but they never count as facts until approved into an entry.
"""

from datetime import UTC, date, datetime
from typing import Any, Literal

from sqlalchemy import JSON, Column
from sqlalchemy.types import DateTime, TypeDecorator
from sqlmodel import Field, SQLModel

TORONTO = "America/Toronto"

CaptureSource = Literal["chat", "strava", "bank_csv"]
# Proposal status: pending, approved, rejected.
# Entry kind: fact, or tombstone (an entry that says "the entry I supersede is deleted").


def utcnow() -> datetime:
    return datetime.now(UTC)


class UTCDateTime(TypeDecorator):
    """Stores datetimes as UTC and hands them back timezone-aware.

    SQLite has no timezone type, so without this a naive datetime would come back
    and nobody could tell whether it meant Toronto or UTC. Naive input is rejected
    instead of guessed.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Any) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("datetimes must be timezone-aware")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect: Any) -> datetime | None:
        return None if value is None else value.replace(tzinfo=UTC)


def utc_column(nullable: bool = False) -> Column:
    return Column(UTCDateTime(), nullable=nullable)


class Capture(SQLModel, table=True):
    __tablename__ = "captures"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())
    source: str = Field(default="chat")
    raw_text: str | None = None
    # Bank CSV hash, so the same file can't be imported twice (v0.3).
    file_hash: str | None = Field(default=None, unique=True)


class Proposal(SQLModel, table=True):
    __tablename__ = "proposals"

    id: int | None = Field(default=None, primary_key=True)
    capture_id: int = Field(foreign_key="captures.id", index=True)
    domain: str
    occurred_at: datetime = Field(sa_column=utc_column())
    payload: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    confidence: float = 1.0
    status: str = Field(default="pending", index=True)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())
    decided_at: datetime | None = Field(default=None, sa_column=utc_column(nullable=True))


class Entry(SQLModel, table=True):
    __tablename__ = "entries"

    id: int | None = Field(default=None, primary_key=True)
    capture_id: int = Field(foreign_key="captures.id", index=True)
    # Empty for imports (Strava, bank CSV), which skip the inbox.
    proposal_id: int | None = Field(default=None, foreign_key="proposals.id")
    kind: str = Field(default="fact")
    domain: str = Field(index=True)
    occurred_at: datetime = Field(sa_column=utc_column())
    tz: str = Field(default=TORONTO)
    payload: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    schema_version: int = 1
    supersedes_id: int | None = Field(default=None, foreign_key="entries.id", index=True)
    # Private by default: nothing reaches a public surface unless it's whitelisted.
    is_private: bool = True
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class Goal(SQLModel, table=True):
    __tablename__ = "goals"

    id: int | None = Field(default=None, primary_key=True)
    domain: str
    metric: str
    target: float
    period: str
    active_from: date
