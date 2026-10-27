# Phase 06: Capture and inbox UI

**Status:** not started · **Who:** Claude

## Goal
Logging from the phone takes under 30 seconds; approving a day's items on desktop takes one click.

## In scope
- Copy first: write every label, placeholder, empty state and error message in DESIGN.md's style, then build.
- Capture page: one text box, submit with Enter or the button, then "Saved · 3 items waiting in inbox". The page is installable to the home screen (manifest + icon only; no offline mode).
- Inbox: one row per proposal with domain label, parsed fields and a low-confidence flag; actions are Edit (inline fields), Reject, and **Approve all** as the one solid button.
- Loading and failure states: if parsing fails, say the text was saved and offer Retry.
- Vitest tests for the inbox approve/edit/reject logic.

## Out of scope
Dashboard numbers (phase 07), deploy.

## Acceptance checks
1. At phone width, type "energy 3 mood 4 slept 2, meal prepped lunch" and submit. You see a confirmation in under about 5 seconds.
2. On desktop, the inbox shows those items. Edit one, reject one, approve all; the inbox shows its empty-state text.
3. With the OpenRouter key removed from `.env`, a capture shows the "saved, retry" message, and the text is in the `captures` table.
4. `pnpm test` passes.
