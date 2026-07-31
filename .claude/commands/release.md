Start the release workflow immediately.

User intent: $ARGUMENTS

## Goal
Run the post-merge release flow after final changes are already merged to `main`:
sync `main` → resolve version → bump both app versions → commit → annotated tag → push → publish GitHub Release → write developer changelog.

## Monorepo Versioning Rule
**One version for the whole repository.** The repo ships as a single product; the apps are not
released independently.

Two files carry the version and must always match:
- `apps/web/package.json` → `version`
- `apps/api/pyproject.toml` → `[project] version`

A release that updates one and not the other is a bug. Verify both after bumping.

## Release Mode Rules
- Always release from `main`.
- If the current branch is not `main`, switch to `main` before any release action.
- Always run `git pull --ff-only origin main` before version/tag operations.
- If the fast-forward pull fails, stop and ask one concise clarification question.

## Version Resolution Rules
- Accept explicit intent values: `patch`, `minor`, `major`, an explicit `vX.Y.Z`/`X.Y.Z`, and the flags `draft` and `--no-bump`.
- Default bump policy (highest-impact wins across included changes):
  - any breaking change → `major`
  - else any feature → `minor`
  - else → `patch`
- Preflight comparison is mandatory before deciding the version:
  - read the version from `apps/web/package.json` **and** `apps/api/pyproject.toml`
  - if the two disagree, stop and ask one concise clarification question
  - read the latest GitHub release tag (fallback: latest remote tag)
  - normalize to semver and compare
  - if the repo version is behind the latest GitHub version, stop and ask
  - if ahead, continue but note the mismatch explicitly in output
- If the user gives no bump/version, infer and propose up to 3 options, then ask for one choice.

## Safety Rules
1. Run `git status --short --branch` first.
2. If there are uncommitted changes, ask one concise clarification question before proceeding.
3. Verify `main` exists on remote.
4. Verify GitHub auth (`gh auth status`).
5. Verify the final release tag does not already exist locally or remotely.
6. Verify the release commit is on `main` before tagging — tag target SHA must equal `main` HEAD.
7. Verify quality gates before publishing:
   - CI for `main` green (if configured and accessible)
   - **any Alembic migration included in this release is called out explicitly** in both the release notes and the developer changelog
8. Never force-push during the release workflow.
9. Never delete or move existing tags unless explicitly requested.

## Release Execution Rules
1. Check clean state and current branch.
2. `git switch main && git pull --ff-only origin main`.
3. Resolve and compare versions:
   - web: `node -p "require('./apps/web/package.json').version"`
   - api: read `version` under `[project]` in `apps/api/pyproject.toml`
   - latest GH release: `gh release list --limit 1 --json tagName --jq '.[0].tagName'`
   - fallback: `git ls-remote --tags --refs origin | sed 's/.*refs\/tags\///' | sort -V | tail -n 1`
4. If not `--no-bump`:
   - update `apps/web/package.json` via `npm version <bump> --no-git-tag-version` (run from `apps/web`)
   - update `version` in `apps/api/pyproject.toml` to the same value
   - confirm both files now read the identical version
   - commit: `chore(release): vX.Y.Z`
5. Create annotated tag on HEAD: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
6. Push: `git push origin main` (if a version commit exists), then `git push origin vX.Y.Z`.
7. Build curated release notes (required — never publish a raw commit list):
   - `## vX.Y.Z Highlights`
   - `## What's New`
   - `## Improvements`
   - `## Fixes`
   - `## Known Issues` (use `None` if none)
   - `## How To Use` (only if there are new flows)
   - `## Compatibility Notes` (breaking changes, migration requirements, or `none`)
   - `## Operational Notes` (rollout/rollback, **database migrations**)
   - `## Full Changelog` with compare URL
   - group by feature/domain (recipes, auth, planning, ingredients), not by commit
   - keep PR/commit references to a short optional appendix
   - omit empty sections
8. Publish: write notes to a temp markdown file, then `gh release create vX.Y.Z --notes-file <path>`; add `--draft` when requested.
9. Generate the developer changelog (required) at `docs/changelog/developer/vX.Y.Z.md`:
   - `# vX.Y.Z Developer Changelog`
   - `## Scope`
   - `## Architecture / Design Changes`
   - `## API and Data Contract Changes`
   - `## Implementation Notes`
   - `## Code Examples` (small focused snippets, only when useful)
   - `## Migrations / Operational Steps`
   - `## Risks and Mitigations`
   - `## Validation and Test Evidence`
   - `## Follow-ups`
   - reference key PRs and relevant files; concise but concrete, no raw commit dumps
10. Post-release verification:
    - tag exists remotely and points to the intended commit
    - release URL accessible, published state matches intent
    - local `main` and `origin/main` both contain the release commit
    - both version files read the released version
11. Return: released version, branch, both app versions before/after, latest GH version before release, comparison result, version commit hash (or `none`), tag name and target commit, release URL, notes summary, developer changelog path, verification results, push results.

## Notes
- Release title stays `vX.Y.Z` unless a custom title is requested.
- Autogenerated notes are source material only; published notes must be curated and human-readable.
- If `--no-bump` was used, call that out explicitly in the final output.
