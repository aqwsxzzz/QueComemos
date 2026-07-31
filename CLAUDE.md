# CLAUDE.md — Que Comemos? (monorepo root)

## Project Overview

- **Product:** recipe sharing between home cooks — see `PRODUCT.md` (read it before any feature work)
- **Type:** monorepo, single developer
- **Delivery:** installable PWA (no app stores, no native shell)
- **Primary language of the product UI/content:** Spanish

```
apps/web/   React 19 PWA        → apps/web/CLAUDE.md
apps/api/   FastAPI + Postgres  → apps/api/CLAUDE.md
docs/       cross-cutting design docs
```

**Read the app-level `CLAUDE.md` before working inside `apps/web` or `apps/api`.** This root file owns only what spans both.

---

## Rule Priority Order

1. App-level `CLAUDE.md` rules for the app you are editing
2. Single Responsibility hard limits (below — applies to both apps)
3. Contract discipline across the web/api boundary (below)
4. Git workflow (below)

---

## Single Responsibility — Hard Limits (both apps)

| Metric | Max | Action |
|--------|-----|--------|
| File length | 200 lines | Split into smaller modules |
| Function / method body | 30 lines | Extract helpers |
| Component JSX return | 50 lines | Extract child components |
| Function parameters | 3 | Use an options object / schema |
| Nesting depth | 3 levels | Early returns or extracted helpers |
| Cyclomatic complexity | 5 branches | Simplify or split |

Pre-flight: can this file be described in one sentence without "and"? If no — split first.

---

## Cross-App Contract Discipline

The API and the web app live in one repo. That is a convenience, **not** permission to blur the boundary.

- The API is the only owner of business rules. The web app never re-derives, synthesizes, or "fixes up" server behavior locally.
- **Never load more data than the current view requires.** If the web app needs filtered/searched/paginated data, add or extend the endpoint in `apps/api` — do not fetch a full list and slice it client-side.
- Expanding a `limit` value to work around missing server-side filtering is a red flag, not a solution.
- When a feature needs new backend behavior: build the endpoint first, then wire the client. Both changes may land in one PR, but the API change is a real API change — schema, validation, tests, migration.
- Types are **not** shared by import across apps. The API's OpenAPI schema is the contract; the web app declares its own types and validates at the boundary.

If a required behavior is backend-owned and missing, the answer is always "add it to `apps/api`" — never a client-side workaround.

---

## Architecture & Boundaries

- Keep separation between UI, state, and data-access layers in `web`; between router, service, and model layers in `api`.
- Make minimal, focused changes tied to the request.
- Follow existing patterns in the feature before introducing new ones.
- Do not add dependencies unless explicitly requested and justified.
- Do not break route/API behavior unless explicitly requested.

---

## Enhance Over Patch

When facing a bug or limitation, prefer enhancing the system over a workaround. Workarounds leave debt; enhancements solve the root cause. When a short-term patch is the only option, mark it explicitly as temporary and document the ideal path.

---

## Tests

**Do not create, modify, or propose frontend tests** unless explicitly requested. Prefer lint + build + typecheck plus manual verification notes.

**Backend tests are expected** for services, guards, and list endpoints — pytest, real Postgres, no DB mocking. See `apps/api/CLAUDE.md`.

---

## Git Workflow

### Branch Naming

Format: `<type>/<short-kebab-description>`

Allowed types: `feat`, `fix`, `refactor`, `chore`, `docs`, `style`, `perf`, `build`, `ci`, `test`

- Description: lowercase, kebab-case, max 5 words
- Always base new branches off `development` unless specified otherwise
- Never branch directly off an existing feature branch unless explicitly requested
- Branch type must match the commit type

### Commit Messages (Conventional Commits)

Format: `<type>(<scope>): <subject>`

**Scope should name the app or feature** — `feat(api/recipe):`, `fix(web/auth):`, `chore(repo):` — so history stays readable in a monorepo.

- Subject: imperative, concise, specific
- Head line max 100 characters
- Add body when context matters (why, impact, migration notes)
- Only use `!` / `BREAKING CHANGE:` for truly breaking changes

Commit workflow:
1. `git status --short --branch`
2. Review diffs
3. Group related changes; avoid mixing unrelated concerns
4. Run validation for **each app touched** (see below)
5. Stage only intended files
6. Commit with a conventional message
7. Push

### Validation Before Commit

| Touched | Run |
|---|---|
| `apps/web` | `npm run lint && npm run build` (in `apps/web`) |
| `apps/api` | `uv run ruff check && uv run mypy src && uv run pytest` |
| Migrations | plus `uv run alembic upgrade head` against a scratch DB |

### PR Workflow

- **Development mode** (default): current branch → `development`
- **Release mode** (`--main`): `development` → `main`

PR body: Summary / What changed / Validation performed (type + status only, no logs) / Risks / Out-of-scope changes explained.
