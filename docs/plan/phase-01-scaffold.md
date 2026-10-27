# Phase 01: Scaffold

**Status:** done · **Who:** Claude

## Goal
An empty but working monorepo: both apps run, both test suites run, CI runs on push.

## In scope
- `git init`, `.gitignore` (`.env`, `*.db`, `*.db-*`, `node_modules`, `.venv`, `dist`), README stub.
- `api/`: uv project pinned to Python 3.13; FastAPI app with `GET /api/health` → `{"ok": true}`; pytest with one test; ruff.
- `web/`: Vite + React + TS with pnpm; a page that calls `/api/health` through the Vite dev proxy and shows the result; Vitest with one test.
- `.github/workflows/ci.yml`: runs pytest and Vitest on push.
- `api/.env.example` listing required variables with fake values.

## Out of scope
Database, LLM, styling, deploy.

## Acceptance checks
1. `cd api && uv run pytest` passes.
2. `cd web && pnpm test` passes.
3. Run `uv run fastapi dev` in `api/` and `pnpm dev` in `web/`. The browser page shows "API ok".
4. `git status` shows no `.env` or `.db` files tracked.
