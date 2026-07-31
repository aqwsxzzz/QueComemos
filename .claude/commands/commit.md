Start the commit workflow immediately.

User intent: $ARGUMENTS

## Branch Step (run first if applicable)
- If user intent starts with `new-branch`, or the current branch is `main`/`master`/`develop`/`development`, or the user states they are on the wrong branch:
  1. Infer the correct branch name from the intent and the changed files using the Branch Naming Rules below.
  2. Run `git switch -c "<branch-name>"` before any staging or committing.
  3. Confirm the new branch is active before proceeding.
- If the current branch is already a feature/fix/chore branch that matches the intent, skip branch creation.

## Branch Naming Rules
- Format: `<type>/<short-kebab-description>`
- Allowed types (match the commit type): `feat`, `fix`, `refactor`, `chore`, `docs`, `style`, `perf`, `build`, `ci`, `test`
- Description: lowercase, kebab-case, max 5 words, no special characters
- Examples: `feat/add-recipe-filter`, `fix/auth-token-refresh`, `chore/update-dependencies`
- Never branch directly off an existing feature branch unless explicitly requested.
- Always base new branches off `development` unless the user specifies otherwise.

## Monorepo Scope Rule
- Commit scope should name the app and/or feature: `feat(api/recipe)`, `fix(web/auth)`, `chore(repo)`, `docs(product)`.
- Prefer splitting a change that touches both apps for unrelated reasons into separate commits. A single feature that legitimately spans both apps may be one commit — name the scope after the feature, not the apps.

## Validation Rule (run before committing)
Determine which apps the staged changes touch, then run:

| Touched | Commands |
|---|---|
| `apps/web` | `npm run lint && npm run build` (from `apps/web`) |
| `apps/api` | `uv run ruff check && uv run mypy src && uv run pytest` |
| `apps/api/migrations` | plus `uv run alembic upgrade head` |
| docs/config only | none required |

Backend commands run inside Docker: `docker compose exec app <command>`.
Skip validation only if the user explicitly requests it.

## Commit Execution Rules
### Commit Message Length Rule
- The commit head (first line) must not exceed 100 characters.
1. Run status and diff review first.
2. Infer the best commit scope and propose up to 3 Conventional Commit messages.
3. Apply Conventional Commit semantic rules only for message correctness; do not do version bumps, changelog updates, or tags.
4. Run the validation commands resolved above.
5. If there is exactly one clear commit path, proceed to stage and commit using the best message.
6. If there is ambiguity (multiple unrelated changes), ask one concise clarification question before committing.
7. After committing, push: `git push -u origin "<branch-name>"` for a new branch, `git push` otherwise.
8. Return: branch used, final message, files committed, validation results, commit hash, push result.

### Out-of-Scope Change Explanation Rule
- If the commit includes changes not reflected in the branch name or intent, briefly explain them in the commit message body.
