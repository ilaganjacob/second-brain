# Second Brain: Life Dashboard Spec

Oct 26, 2026 · Jacob Ilagan · Updated Oct 27, 2026 with the decisions from the review rounds.

## Overview

A personal second brain. You type what you did, an LLM turns it into structured data, you approve it, and a dashboard shows progress against your goals. It's built to grow for years, to teach system design along the way, and to double as a portfolio piece.

**Three goals, in priority order**

1. **Use it daily.** If logging takes more than a minute or two a day, the project fails no matter how good it looks.
2. **Learn system design by need.** Each concept (queues, caching, event sourcing) is added only when a real problem forces it, then written up as an ADR.
3. **Showcase it.** A public demo with fake data plus a case-study page, without ever exposing private data.

**Guiding principles**

- Input is the hard problem, not display. Optimize capture first.
- Machines collect what they can (Strava, bank CSV). You type only what they can't.
- Raw captures and approved entries are immutable and are the source of truth. Everything else can be rebuilt.
- Retrieval over organization: ask your data questions instead of maintaining folder trees.
- Public and private are separated by structure, not by remembering to hide things.

## Domains, metrics and goals

| Domain | Key metrics | Goal | Input | Phase |
| --- | --- | --- | --- | --- |
| Job applications | Applications per week, pipeline by stage, follow-ups due | 10 applications / week | Capture | v0.1 |
| Eating | Meals prepped vs ate out | none yet | Capture | v0.1 |
| Daily check-in | Energy, mood, sleep quality (1–5 each) | none, trend only | Capture, at 21:00 for the same day | v0.1 |
| Spending (typed) | Total by category, month vs goal | $1,000 CAD / month | Capture, provisional until bank import | v0.1 |
| Notes | Anything that fits no domain | — | Capture (catch-all) | v0.1 |
| Workouts (Zwift, outdoor) | Ride hours, distance, power, heart rate | 8 h / week | Strava import only | v0.2 |
| Salary and savings | Monthly balance snapshot, savings trend | — | Manual monthly entry | v0.2 |
| Learning | LeetCode solved by topic/difficulty, hints needed, project hours | none (dropped) | Capture | v0.2 |
| Freelance pipeline | Leads, proposals sent, stage | — | Capture (reuses applications model) | v0.2 |
| Spending (bank) | Same as above, now authoritative | $1,000 CAD / month | Wealthsimple CSV import | v0.3 |

**Out of scope for now:** habit streaks, journaling, nutrition macros, native mobile app. The phone gets a capture page, not an app.

**Fixed facts**
- Timezone: America/Toronto. Store `occurred_at` in UTC plus the IANA zone. Resolve "today" and "yesterday" in Toronto time.
- Currency: CAD only. Bank: Wealthsimple.
- Check-in reminder: a repeating phone reminder at 21:00, no code. The check-in rates that same day; sleep quality rates the previous night.

## Capture pipeline

One LLM call with structured output does both the parsing and the categorizing. A `domain` field routes each entry.

1. You type: "applied to Shopify for frontend dev, $14 lunch, energy 3 mood 4 slept 2".
2. `POST /capture` stores the raw text in `captures`, then calls the LLM with a JSON schema. The prompt includes today's date (Toronto) and your open applications.
3. The model returns a list of typed items. Pydantic validates them.
4. Each item becomes a **proposal** with status `pending` and lands in the inbox.
5. In the inbox you approve, edit then approve, or reject. **Approve all** handles the normal case.
6. Approving a proposal writes an immutable **entry** linked to its capture.

**Rules**

- Always keep `raw_text`, so old captures can be re-parsed when the schema improves.
- Nothing reaches `entries` without approval. A misparse (14 as minutes, not dollars) poisons trust in the data.
- One phrase can create several entries: "$14 lunch" becomes a spending entry plus an eating (ate out) entry, linked by capture.
- Anything the model can't place becomes a `note`. Every item carries a `confidence`; low confidence is flagged in the inbox. The model never guesses silently.
- Typed rides become notes, not workouts. Workouts come only from Strava, so there are no duplicates.
- Typed spending is provisional. The bank import (v0.3) matches it on amount ±1 day and supersedes it.
- Applications are matched to existing ones by company **and** job title. The model returns an `application_id` when it updates an existing application.
- Follow-up dates are set automatically: applied +7 days, screen or interview +3 days.
- The model provider sits behind one interface. v0.1 uses **OpenRouter**, pinned to one model, with `require_parameters: true` (only route to providers that support structured output) and `data_collection: "deny"`.

## Data model

Raw captures and approved entries are append-only. Everything else is derived, or is a workflow state that never counts as a fact.

| Table | Purpose | Key columns |
| --- | --- | --- |
| `captures` | Every chat message or import batch, never edited | id, created_at, source (chat, strava, bank_csv), raw_text, file_hash |
| `proposals` | Parsed items waiting in the inbox (mutable workflow state, not facts) | id, capture_id, domain, payload (JSON), confidence, status (pending, approved, rejected), created_at |
| `entries` | Approved facts, append-only | id, capture_id, proposal_id, occurred_at, tz, domain, payload (JSON), schema_version, supersedes_id, is_private |
| `goals` | Targets that make "optimize" measurable | id, domain, metric, target, period (week, month), active_from |
| `reviews` | Weekly summaries (v0.4) | id, week_start, llm_summary, my_reflection |

**Design notes**

- **Corrections:** a fix is a new entry with `supersedes_id` pointing at the old one. A delete is a tombstone entry. The app never runs UPDATE or DELETE on `entries`.
- **Applications are not a table in v0.1.** Every application event (applied, moved to screen, rejected) is an entry. Current stage and follow-up dates are computed from those events when read. A cached `applications` table comes only if that query gets slow, and that's an ADR.
- `schema_version` on every entry, so old payloads still validate after the schema changes.
- Import idempotency: `file_hash` on bank CSVs and the Strava activity id as a unique key, so re-importing never duplicates.
- SQLite file on a Fly.io volume, continuously backed up to Cloudflare R2 with Litestream from v0.1. Postgres only if ever needed.

## Public and private

One codebase, three surfaces. The public side never connects to the real database.

| Surface | Data | Access | Phase |
| --- | --- | --- | --- |
| Private app | Real data, everything | Behind Cloudflare Access, only you | v0.1 |
| Demo mode | Seeded fake data with realistic patterns | Public, full UI | v1 |
| Now page | A whitelisted handful of metrics (ride hours this month, applications sent) | Public, read-only | v1 |

**Rules**

- Demo mode runs against a separate database file, never a filter on the real one. Demo capture uses canned parses for preset inputs. Free text is rate-limited and uses the cheapest model.
- The now page reads a static `now.json` that a scheduled job exports. Adding a metric is an explicit code change.
- Money privacy mode: dollar figures are blurred by default; the `$` key reveals them.
- Auth: Cloudflare Access (email one-time code) in front of `brain.jacobilagan.com`. The API also checks the Access JWT on every request, so the raw Fly.io URL can't be used to bypass login.

## Insight layer

1. **Weekly review (v0.4).** A scheduled job sends the week's entries and goals to the LLM, which writes a short summary in the design study's copy rules: exact numbers, no cheerleading. You add a reflection.
2. **Ask your data (v1).** Questions become SQL, run on a read-only connection (`mode=ro`, `PRAGMA query_only`, an authorizer that blocks private columns). The answer shows the query it ran.
3. **Correlations (v1+).** After about three months of data, plain pandas comparisons: energy vs ride hours, spending vs heavy job-search weeks. No ML until simple stats stop being enough.

All three use the same small internal API, so an external agent (Claude via MCP, for example) can query the dashboard later.

## Stack and hosting

| Layer | Choice | Why |
| --- | --- | --- |
| Frontend | React + TypeScript + Vite, pnpm | Learning goal; TS carries over from Angular |
| Charts (v0.2) | Recharts | Plain React components, easy to theme with tokens |
| Backend | FastAPI + Pydantic + SQLModel, uv, Python 3.13 | Pydantic doubles as the structured-output schema |
| Database | SQLite on a Fly.io volume, Litestream to R2 | One file, zero ops, continuous backups |
| Jobs | APScheduler, a real queue only when needed | Weekly reviews and imports |
| LLM | OpenRouter behind a provider interface | Swap models without code changes |
| Hosting | Frontend on Cloudflare Pages at `brain.jacobilagan.com`; a Pages Function proxies `/api/*` to the FastAPI app on Fly.io | One origin and one login; no CORS |
| Tests and CI | pytest, Vitest, GitHub Actions | Required for the public repo |

## Design system

See [DESIGN.md](DESIGN.md). In short, the Lexington study's rules adapted for a dark-only dashboard: Switzer at 400/500, a rust accent used only on off-goal or due items, report-style rows instead of cards, no shadows or gradients, exact-number copy.

## System design learning map

Each feature teaches one interview-relevant concept. Add the concept only when the feature forces it, then write an ADR.

| Feature | Concept | Trigger to add it |
| --- | --- | --- |
| Capture, parse, inbox | Ingestion pipelines, validation at boundaries | v0.1 |
| Append-only entries, computed views | Event sourcing, CQRS | v0.1 (corrections), first schema change |
| Strava and bank imports | ETL, idempotency | First duplicate import |
| LLM calls off the request path | Job queues, retries, backoff | Capture feels slow or an LLM call times out |
| Weekly review | Scheduled workers | v0.4 |
| Dashboard aggregates | Caching, materialized views | A page takes more than about a second |
| Public vs private | Auth, authorization, data isolation | v0.1 deploy |
| Ask your data | Text-to-SQL, least privilege | v1 |
| Logs and errors | Observability, structured logging | First bug you can't reproduce |

**ADRs:** one short markdown file per decision in `docs/adr/`, numbered. Format: context, decision, alternatives considered, consequences. The ADRs due at the end of v0.1:

1. SQLite on Fly.io over Postgres
2. One LLM call over two (parse and categorize together)
3. Proposals table: inbox state kept separate from immutable entries
4. Cloudflare Access + JWT check instead of custom auth
5. OpenRouter as the provider layer

## Roadmap

Each phase ends with a usage test, not a feature checklist. A phase is done when you're actually using it; then you write its ADRs and move on.

| Phase | What you get | Done when |
| --- | --- | --- |
| v0.1 | Capture box, AI parse, inbox, dashboard for applications, check-in, eating, typed spending. Full design system. Live with login, usable from the phone. | You've logged 7 days in a row |
| v0.2 | Strava import, savings snapshot, learning, freelance leads, goals editing, first charts | 2 more weeks of daily use; ride hours showing |
| v0.3 | Wealthsimple CSV import, merchant rules + AI fallback, reconciliation with typed spending | 1 month of spending, no duplicates |
| v0.4 | Weekly AI review with your reflection | 4 weekly reviews written |
| v1 | Ask your data, public demo, now page, case study | Link is on your resume and site |
| v1+ | Correlations | 3 months of data, one real insight |
