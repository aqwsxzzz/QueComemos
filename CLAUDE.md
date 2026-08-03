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

1. Installed skills in `.claude/skills/` — they own code-level craft (structure, size limits, framework idiom, SQL, security, testing technique)
2. App-level `CLAUDE.md` rules for the app you are editing
3. Contract discipline across the web/api boundary (below)
4. Project delivery rules (below — validation, scope conventions, PR body)

Where a skill and a local rule cover the same ground, **the skill wins**. Local rules exist to add what the skills cannot know about this project, not to restate them.

---

## Code Structure

Owned by the `code-structure` skill (size limits, SRP, Rule of Three) and the `react` skill (component splitting, JSX return size). Do not restate those limits here.

Pre-flight, still project policy: can this file be described in one sentence without "and"? If no — split first.

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

The `testing-best-practices` skill owns **how** a test is written. This section owns **when** one gets written — the two do not conflict.

**Do not create, modify, or propose frontend tests** unless explicitly requested. Prefer lint + build + typecheck plus manual verification notes.

**Backend tests are expected** for services, guards, and list endpoints — pytest, real Postgres, no DB mocking. See `apps/api/CLAUDE.md`.

`/test-review` verifies existing tests actually catch regressions; it does not override the frontend rule above.

---

## Git Workflow

**`/ship` owns the pipeline** — commit → PR → merge → release, including branch naming, conventional commits, secret scanning, merge safety, semver and the changelog. Do not run those steps by hand.

- `/ship` — interactive, confirms at each stage boundary
- `/ship pr` — through PR creation, then stop
- `/ship release` — the full pipeline (this replaces the old `--main` release mode)

The base branch is `development`; `/ship` detects it. Releases go `development` → `main`.

Everything below is what `/ship` cannot infer about this repo. It still applies.

### Validation Before Commit

`/ship` has **no validation stage** — run this before letting it commit.

| Touched | Run |
|---|---|
| `apps/web` | `npm run lint && npm run build` (in `apps/web`) |
| `apps/api` | `uv run ruff check && uv run mypy src && uv run pytest` |
| Migrations | plus `uv run alembic upgrade head` against a scratch DB |

Backend commands run inside Docker: `docker compose exec app <command>`. Skip validation only when explicitly asked to.

### Monorepo Commit Scope

Scope names the app and/or feature — `feat(api/recipe):`, `fix(web/auth):`, `chore(repo):`, `docs(product):` — so history stays readable. Head line max 100 characters.

Split a change touching both apps for unrelated reasons into separate commits. One feature that legitimately spans both may be a single commit — scope it after the feature, not the apps.

### PR Body

Summary / What changed (grouped by app when it spans both) / Validation performed (type + status only, never logs or output) / Migrations (name the Alembic revisions, or `none`) / Risks / Out-of-scope changes explained.

<!-- claude-skills:skill-evaluation:start -->
## Skills

BEFORE writing ANY code, you MUST:

1. List EVERY skill available: check `.claude/skills/` (project) and `~/.claude/skills/` (global). The system-reminder's available-skills section is a hint, not the source of truth — if it's missing or empty, still check the directories.
2. For each skill, write: [skill-name] → ACTIVATE / SKIP — [one-line reason]
3. Call Skill(name) for every skill marked ACTIVATE
4. Emit the literal token `[skills-checked]` on its own line
5. Only THEN proceed to implementation

A PreToolUse gate hook blocks Write/Edit/MultiEdit until the `[skills-checked]` token appears in your response since the most recent user prompt. The gate fires once per turn — the first blocked edit is the signal to evaluate skills, then retry. If you skip the evaluation, your response is INCOMPLETE and WRONG.
<!-- claude-skills:skill-evaluation:end -->

<!-- claude-skills:file-size:start -->
## File Size Enforcement

- **Never write a file longer than 200 lines of code.** If a file would exceed 200 lines, split it into smaller modules before writing.
- This rule applies during skill evaluation: if the code you're about to write would exceed 200 lines in any single file, refactor into multiple files first.
- Skill evaluation must check this limit as part of every ACTIVATE decision.
<!-- claude-skills:file-size:end -->
