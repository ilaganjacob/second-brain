# Phase 04: Capture and inbox API

**Status:** not started · **Who:** Claude writes it, explaining choices; you review

## Goal
The full flow over HTTP: capture → proposals → approve → entries, plus the read endpoints the dashboard needs.

## In scope
- `POST /api/capture` `{text}`: stores the capture, parses it, stores the proposals, returns them. If the LLM fails, the capture is still saved and the response says to retry. (Raw text is never lost.)
- `GET /api/inbox`: pending proposals, newest first.
- `POST /api/proposals/{id}/approve` (optionally with edited payload), `POST /api/proposals/{id}/reject`, `POST /api/inbox/approve-all`.
- `POST /api/entries/{id}/supersede` and `POST /api/entries/{id}/delete` (creates a tombstone).
- `GET /api/dashboard`: everything phase 07 shows, computed from current entries:
  - applications this week vs goal; pipeline by stage; follow-ups due with dates (applied +7 d, screen/interview +3 d);
  - check-in today and the 7-day averages;
  - meals this week: prepped vs ate out;
  - spending this month vs goal, by category, flagged "typed only";
  - inbox count.
- Week = Monday–Sunday, Toronto time.

## Out of scope
Auth (phase 08), UI.

## Acceptance checks
1. `uv run pytest` passes, with at least one test per route, using FakeProvider.
2. In the FastAPI docs page (`/docs`), capture "applied to Shopify for frontend dev, $14 lunch", approve all, and see `/api/dashboard` show 1 application, 1 ate-out meal and $14 spent, with a Shopify follow-up due in 7 days.
3. Capture "Shopify moved me to interview". It updates the same application, and the follow-up moves to +3 days.
