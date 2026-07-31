# Que Comemos?

Recipe sharing between home cooks. Not restaurant food — the meals people actually cook.

Installable PWA. Spanish-first.

## Repository layout

```
apps/web/    React 19 + TypeScript PWA (Vite, TanStack Query/Router, Zustand, shadcn/ui, Tailwind)
apps/api/    FastAPI + SQLAlchemy async + Postgres (uv, Alembic, Pydantic v2)
docs/        cross-cutting design documents
```

## Start here

| Document | What it covers |
|---|---|
| [PRODUCT.md](PRODUCT.md) | What we're building, why, and what's deliberately out of scope |
| [CLAUDE.md](CLAUDE.md) | Monorepo rules — shared limits, cross-app contract, git workflow |
| [apps/web/CLAUDE.md](apps/web/CLAUDE.md) | Frontend rules |
| [apps/api/CLAUDE.md](apps/api/CLAUDE.md) | Backend rules |
| [docs/ingredients-model.md](docs/ingredients-model.md) | The ingredient/alias design — read before touching recipe data |

## Status

Scaffolded. Neither app is implemented yet — phase A (recipes & community) is next.

## Development

```bash
# web
cd apps/web && npm install && npm run dev

# api (runs in Docker)
docker compose up
docker compose exec app uv run alembic upgrade head
```

Both apps are versioned together; see `.claude/commands/release.md`.
