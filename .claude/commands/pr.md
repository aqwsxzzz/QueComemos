Start the pull request workflow immediately.

User intent: $ARGUMENTS

## Mode Selection
- If user intent contains `--main` or `--master`, run in release mode:
  - Head branch: `development`
  - Base branch: `main`
  - Remove `--main`/`--master` from the final PR title/body text
- Otherwise run in development mode:
  - Head branch: current checked-out branch
  - Base branch: `development`

## Target Rules
- Development mode: never open a PR from `main`, `master`, `develop`, or `development` to `development`; if currently on one of these, ask for one concise clarification before proceeding.
- Release mode: always create PR from `development` to `main` unless the user explicitly overrides.

## PR Execution Rules
1. Run `git status --short --branch` and confirm there are no merge conflicts.
2. Resolve head/base branches from Mode Selection.
3. If release mode:
   - Capture the current branch name so it can be restored after sync.
   - Run `git switch development && git pull --ff-only origin development`.
   - Run `git switch main && git pull --ff-only origin main`.
   - Return to the previous branch unless it is `development` or `main`.
4. Verify the head branch is pushed to origin; if not, push with upstream first.
5. Compare head against base and summarize changes (commits/files) for PR context.
6. If release mode, generate PR title/body only from the real `main...development` diff after pulls.
7. Propose up to 3 PR titles if intent is ambiguous; otherwise use the best clear title.
8. Build a concise PR body with:
   - Summary
   - What changed — **grouped by app** (`apps/web`, `apps/api`, docs) when the PR spans both
   - Validation performed — list only validation type and status (Passed/Failed). Do not paste command output, logs, stack traces, or code snippets.
   - Migrations — name any Alembic revisions included, or state `none`
   - Risks/notes
   - Explain any out-of-scope changes not reflected in the branch name or PR intent
9. Create the PR using the resolved head/base branches:
   - Default: ready PR
   - If user intent includes `draft`, create as draft
10. Return: base and head branches, final title, PR URL, draft/ready state, follow-up actions.

## Safety Rules
- If there are uncommitted changes that would affect PR accuracy, ask one concise clarification question before creating the PR.
- Development mode: if `development` does not exist on remote, ask one concise clarification question and suggest `develop` as a fallback.
- Release mode: if `main` or `development` does not exist on remote, ask one concise clarification question before proceeding.
- Release mode: if `git pull --ff-only` fails on either branch, stop and ask one concise clarification question.
