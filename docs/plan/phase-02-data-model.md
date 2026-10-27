# Phase 02: Data model

**Status:** not started · **Who:** Claude

## Goal
The tables from SPEC.md exist, entries can only ever be appended, and goals are seeded.

## In scope
- SQLModel models: `captures`, `proposals`, `entries`, `goals` (`reviews` waits for v0.4).
- SQLite file at a path from env (`DATABASE_PATH`), created on startup. WAL mode on. (Litestream needs it, and it lets reads and writes overlap.)
- A small repository layer: `add_capture`, `add_proposals`, `approve_proposal` (creates an entry), `reject_proposal`, `supersede_entry`, `tombstone_entry`. There's no update or delete function for entries at all.
- Timestamps: `occurred_at` stored in UTC with `tz = "America/Toronto"`.
- Seed goals: 10 applications/week, $1,000 spending/month, 8 ride hours/week (shown from v0.2).
- Tables created with `create_all`. Migrations (Alembic) wait until the first schema change, which gets an ADR.

## Out of scope
HTTP routes, LLM.

## Acceptance checks
1. `uv run pytest` passes, including tests that:
   - approving a proposal creates exactly one entry linked to the capture and the proposal;
   - superseding an entry leaves the original row unchanged;
   - a tombstone hides an entry from the "current entries" query;
   - Toronto times round-trip correctly across midnight UTC.
2. Delete the `.db` file and start the API. It recreates the file with seeded goals.
