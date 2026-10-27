"""Engine setup, schema creation and seed data."""

import os
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Engine, event, text
from sqlmodel import Session, SQLModel, create_engine, select

from api.models import TORONTO, Goal

DEFAULT_DATABASE_PATH = "second-brain.db"

# The database refuses edits to facts, so "append-only" doesn't rely on every
# future code path remembering the rule.
APPEND_ONLY_TRIGGERS = [
    f"""
    CREATE TRIGGER IF NOT EXISTS {table}_no_{op.lower()}
    BEFORE {op} ON {table}
    BEGIN
        SELECT RAISE(ABORT, '{table} is append-only');
    END
    """
    for table in ("captures", "entries")
    for op in ("UPDATE", "DELETE")
]

SEED_GOALS = [
    {"domain": "application", "metric": "count", "target": 10, "period": "week"},
    {"domain": "spending", "metric": "amount_cad", "target": 1000, "period": "month"},
    # Shown from v0.2, when the Strava import exists.
    {"domain": "workout", "metric": "hours", "target": 8, "period": "week"},
]


def make_engine(path: str | None = None) -> Engine:
    path = path or os.environ.get("DATABASE_PATH", DEFAULT_DATABASE_PATH)
    engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(dbapi_conn, _record):
        cursor = dbapi_conn.cursor()
        # WAL lets the dashboard read while a capture writes; Litestream needs it too.
        cursor.execute("PRAGMA journal_mode=WAL")
        # SQLite ignores foreign keys unless asked.
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def init_db(engine: Engine) -> None:
    """Create tables and triggers, and seed goals on an empty database.

    create_all is enough until the first schema change; that change brings in
    Alembic and an ADR.
    """
    SQLModel.metadata.create_all(engine)
    with engine.begin() as conn:
        for trigger in APPEND_ONLY_TRIGGERS:
            conn.execute(text(trigger))
    with Session(engine) as session:
        if session.exec(select(Goal)).first() is None:
            today = datetime.now(ZoneInfo(TORONTO)).date()
            session.add_all(Goal(active_from=today, **goal) for goal in SEED_GOALS)
            session.commit()
