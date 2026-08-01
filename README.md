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

**Phase A (recipes & community) is implemented.** Accounts, recipe authoring with
structured ingredients, process photos, the public pool with server-side search and
pagination, follows, favorites, comments (including step-level questions), and
moderation — reports, blocks and takedowns.

Phase C (meal planning + shopping list) is next. Phase B (pantry) stays cut.

## Development

```bash
# api + database + object storage
docker compose up
docker compose exec app uv run alembic upgrade head
docker compose exec app uv run python -m quecomemos.scripts.seed   # ingredient taxonomy

# web
cd apps/web && npm install && npm run dev
```

| Service | URL |
|---|---|
| Web (dev) | http://localhost:5173 |
| API docs | http://localhost:8000/api/v1/docs |
| MinIO console | http://localhost:9001 |

Photo storage is MinIO locally and Cloudflare R2 in production — the same S3 code
path, differing only by environment variables.

## Validation

```bash
docker compose exec app uv run ruff check
docker compose exec app uv run mypy src
docker compose exec app uv run pytest

cd apps/web && npm run lint && npm run build
```

Both apps are versioned together; see `.claude/commands/release.md`.
