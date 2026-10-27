# Phase 03: Parser

**Status:** not started · **Who:** Claude writes it, explaining choices; you review

## Goal
Text in, validated typed items out, tested against 20 real sentences before any route uses it.

## In scope
- Pydantic models for v0.1 items: `ApplicationEvent` (company, role, stage, application_id optional), `Meal` (kind: prepped / ate_out / home), `CheckIn` (energy, mood, sleep 1–5), `Spending` (amount CAD, category, merchant), `Note` (text). Each has `domain`, `occurred_at` and `confidence`.
- A discriminated union of those items, applied to each list item. (This fixes the bug in the original spec snippet, where the discriminator was on the list instead of its items.)
- An `LLMProvider` interface with two implementations: `OpenRouterProvider` and a `FakeProvider` for tests.
- A prompt builder that adds today's date in Toronto time, your open applications (id, company, role, stage) and the rules from SPEC.md (rides become notes, "$14 lunch" becomes two items, uncertain text becomes a note).
- `fixtures/samples.txt`: 20 sentences in your own words, including tricky ones ("14 zwift", "yesterday", "Shopify moved me to interview").
- `scripts/try_parser.py`: runs all samples against the real model and prints a table.
- Pick the model: try two cheap models on OpenRouter and keep the one that gets the samples right.

## Out of scope
Routes, the database, UI.

## Acceptance checks
1. `uv run pytest` passes with FakeProvider, including validation failures (e.g. energy 7 is rejected).
2. `uv run python scripts/try_parser.py` gets at least 18 of 20 samples right by your judgment, with no silent misparses. Wrong ones must at least be low-confidence or notes.
3. The chosen model id is set in `.env.example`, and the result goes in a short note for ADR 5.
