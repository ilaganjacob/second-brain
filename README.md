# Second Brain

Type what you did, approve it, see progress against your goals. Scope: [docs/SPEC.md](docs/SPEC.md). Design: [docs/DESIGN.md](docs/DESIGN.md). Plan: [docs/plan/PLAN.md](docs/plan/PLAN.md).

## Run locally

```bash
cd api && uv run fastapi dev   # API on :8000
cd web && pnpm dev             # web on :5173, proxies /api to :8000
```

## Test

```bash
cd api && uv run pytest
cd web && pnpm test
```
