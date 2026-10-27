# Phase 08: Deploy

**Status:** not started · **Who:** Claude, with account steps by you (see "Before you start" in PLAN.md)

## Goal
The app runs at `brain.jacobilagan.com`, only you can get in, and the database is backed up continuously.

## In scope
- **API on Fly.io:** Dockerfile, `fly.toml`, a 1 GB volume for SQLite, the smallest machine size, region `yyz` (Toronto). Secrets set with `fly secrets`.
- **Backups:** Litestream in the same container replicating to a Cloudflare R2 bucket, plus a documented restore command.
- **Web on Cloudflare Pages:** built from `web/`, custom domain `brain.jacobilagan.com`, with a Pages Function that proxies `/api/*` to the Fly app. One origin, so no CORS.
- **Login:** a Cloudflare Access application on `brain.jacobilagan.com`, email one-time code, allowing only your email.
- **API guard:** FastAPI checks the `Cf-Access-Jwt-Assertion` header against your Access team's public keys, so a request straight to the `*.fly.dev` URL gets a 401.
- GitHub Actions deploys the API to Fly on push to `main`. Pages deploys the web automatically.
- Write the five v0.1 ADRs.

## Out of scope
Demo mode, now page, Strava.

## Acceptance checks
1. On your phone, open `brain.jacobilagan.com`, log in with the email code, capture something, and see it in the inbox on desktop.
2. Opening the `*.fly.dev` API URL directly returns 401.
3. In a private window, `brain.jacobilagan.com` asks for login and shows no data.
4. Delete the local copy, restore from R2 with the documented command, and the data is all there.
5. `docs/adr/0001`–`0005` exist.

**Then v0.1's real test starts:** log 7 days in a row.
