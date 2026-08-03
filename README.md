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

Both apps run from the same Compose file. One command starts everything:

```bash
docker compose watch
```

That builds and starts Postgres, MinIO, the API and the web app, then syncs source
changes into the containers — the API reloads via uvicorn, the web app via Vite HMR.

First run only:

```bash
docker compose exec app uv run alembic upgrade head
docker compose exec app uv run python -m quecomemos.scripts.seed   # ingredient taxonomy
```

`docker compose up -d` also works if you don't want file syncing. API code is bind
mounted so it still reloads; the web app will serve whatever was in the image at
build time.

| Service | URL |
|---|---|
| Web | http://localhost:5175 |
| API docs | http://localhost:8000/api/v1/docs |
| MinIO console | http://localhost:9001 |

Prefer running the web app on the host? `cd apps/web && npm install && npm run dev`
still works — stop the `web` service first so port 5175 is free.

### Ports

Chosen so this project can run alongside the other local apps:

| Port | Service | Note |
|---|---|---|
| 5175 | web dev server | 5173 is Ovejitas, 5174 is DocTrack; `strictPort` fails loudly on a clash |
| 8000 | API | Ovejitas uses 7777, DocTrack publishes 8001 |
| 5432 | Postgres | Ovejitas uses 5433/5436, DocTrack uses 5434 |
| 9000 / 9001 | MinIO API / console | |

If you change the web port, change `ALLOWED_ORIGINS` for the API too — otherwise
the browser hits a CORS wall with no obvious cause.

### Production image

`apps/web/Dockerfile` has a `prod` target that builds the app and serves it from
unprivileged nginx with SPA fallback and correct service-worker caching:

```bash
docker build --target prod -t quecomemos-web ./apps/web
```

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
