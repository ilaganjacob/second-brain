# v0.1 Plan

**Goal:** type what you did (from your phone or desktop), approve it in an inbox, and see exact numbers against your goals on a designed dashboard. Live at `brain.jacobilagan.com` behind login.

**v0.1 is done when** you've logged 7 days in a row and the five v0.1 ADRs are written (see SPEC.md).

Each phase leaves the app runnable and has checks you can do in a few minutes. Claude implements one phase, then stops until you confirm the checks pass.

| # | Phase | Who writes it | Status |
| --- | --- | --- | --- |
| 01 | [Scaffold](phase-01-scaffold.md) | Claude | done |
| 02 | [Data model](phase-02-data-model.md) | Claude | done |
| 03 | [Parser](phase-03-parser.md) | Claude, you review | not started |
| 04 | [Capture and inbox API](phase-04-capture-api.md) | Claude, you review | not started |
| 05 | [Design system and shell](phase-05-design-shell.md) | Claude | not started |
| 06 | [Capture and inbox UI](phase-06-capture-inbox-ui.md) | Claude | not started |
| 07 | [Dashboard](phase-07-dashboard.md) | Claude | not started |
| 08 | [Deploy](phase-08-deploy.md) | Claude, plus account steps by you | not started |

Statuses: not started → in progress → awaiting-verification → done.

**03 and 04:** the spec originally had you writing the capture route and schema yourself. To keep the one-day timeline, Claude writes them and explains each choice, and you review them closely, since they're the core of the system.

## Before you start (you)

Things only you can do. Phases 01–07 need only the first two; phase 08 needs the rest.

1. Install tools: `brew install uv flyctl` (Node 24, pnpm and git are already installed).
2. Create an OpenRouter account, add about $5 of credit, and create an API key. Put it in `api/.env` as `OPENROUTER_API_KEY=...` once phase 01 creates the folder.
3. Create a Fly.io account. It needs a card; expect about $3–5/month.
4. Check that `jacobilagan.com` uses Cloudflare for DNS. Cloudflare Access only works on domains Cloudflare manages.
5. Create the GitHub repo `second-brain` (public). Claude can do it with `gh` if you'd like.

## Open questions

- Is `brain.jacobilagan.com` the final subdomain?
