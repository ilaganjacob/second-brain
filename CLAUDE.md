# Second Brain

Full scope: docs/SPEC.md. Design: docs/DESIGN.md. Current phase: v0.1 (plan in docs/plan/PLAN.md).

## Stack
React + TS + Vite + pnpm (web/), FastAPI + Pydantic + SQLModel + SQLite with uv, Python 3.13 (api/).
Hosting: Cloudflare Pages (web, plus a Pages Function proxying /api/*) and Fly.io (api, SQLite volume, Litestream to R2).
LLM: OpenRouter behind a provider interface.

## Rules
- Work one roadmap phase at a time, and one plan phase at a time; do not build ahead.
- I am learning: explain design choices briefly as you go.
- Every new decision gets an ADR in docs/adr/.
- Never write to entries without an approved proposal. Never UPDATE or DELETE entries; use supersedes_id or a tombstone.
- Never add a field to public endpoints without asking.
- Tests for every API route.
- Follow docs/DESIGN.md: tokens only, no hardcoded colors, no shadows or gradients, accent only for off-goal or due.
- Write UI copy with exact numbers, never cheerleading.
- Never commit real data, .env files or *.db files.
