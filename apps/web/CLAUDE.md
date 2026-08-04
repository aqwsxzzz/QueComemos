# CLAUDE.md — apps/web (PWA)

Read `../../CLAUDE.md` (root) and `../../PRODUCT.md` first. This file owns frontend rules only.

## Stack

React 19, TypeScript 5.x strict, TanStack Query, TanStack Router, Zustand, shadcn/ui, Tailwind CSS, Vite. Package manager: npm.

```bash
npm run lint       # ESLint
npm run build      # TypeScript + Vite build
npm run typecheck  # Type check only
```

Always run `npm run lint && npm run build` before committing.

## PWA obligations

This is the whole product on mobile — installability and offline behavior are features, not polish.

- Manifest + service worker are part of the build, not an afterthought.
- Design mobile-first. Touch targets, thumb reach, and one-handed use are real constraints.
- Recipe **authoring** is the one flow that should also be comfortable on a large screen.
- **No push notifications, no reminders.** See `PRODUCT.md` — this is a product decision, not a gap.

---

## Rule Priority Order

1. useEffect Rule — **highest priority**
2. UI Consistency & Reuse Gate
3. Single Responsibility hard limits (root `CLAUDE.md`)
4. Data fetching rules
5. React & TypeScript best practices

---

## 1. useEffect — Escape Hatch Only (Highest Priority)

`useEffect` is only for synchronizing with **external systems**. Never use it for:
- Derived state
- Prop-sync or state resets (use component `key` instead)
- Event-specific logic (use event handlers)
- Parent notifications
- Chained state transitions
- Server data fetching (use TanStack Query)

Decision gate before writing `useEffect`:
1. Can this be calculated during render?
2. Is this an expensive derivation → `useMemo`?
3. Should state reset by changing component `key`?
4. Is this user interaction logic → event handler?
5. Is this external store subscription → `useSyncExternalStore`?
6. Is this server data → TanStack Query?
7. Is this truly synchronization with an external system?

Only write `useEffect` when **item 7 is true**. Always include complete dependencies and cleanup for subscriptions/listeners/timers. For async effects, use an ignore/abort pattern.

---

## 2. Shadcn-First UI Rule

Always use existing shadcn/ui components from `src/components/ui/` when an equivalent exists.

- Never introduce raw HTML controls (`input`, `select`, `textarea`, `button`, form wrappers, modal primitives, cards, labels, separators) when shadcn components cover the case.
- Compose shadcn primitives: `Form`, `FormField`, `Input`, `Button`, `Card`, `Dialog`, `Select`, `Label`, `Separator`.
- Only fall back to native HTML/CSS when no shadcn path exists — document the reason.

---

## 3. UI Consistency & Reuse Gate (Mandatory)

Before creating or editing any UI element (buttons, badges, cards, chips, action links, toggles):

1. Is there an existing shared component for this element type?
2. Is there an existing semantic variant that matches this intent?
3. Can I reuse `src/components/ui/*` without local color overrides?
4. If no, should I add a new semantic variant in the shared component instead?
5. If still no, is this a real product requirement for a unique design?

Only add local custom styling when **step 5 is true**.

- No `className` color overrides (`bg-*`, `text-*`, `border-*`) on reusable primitives for core intent states.
- Extend shared variant definitions in `src/components/ui/button.tsx`, `badge.tsx`, etc.
- One intent = one visual language app-wide.
- Design tokens only — no hardcoded hex values.

---

## 4. Data Fetching — Server-First, Just-in-Time

**Never load more data than the current view requires.**

- Prefer API endpoints that filter, search, and paginate server-side over fetching lists and slicing client-side.
- Use `useInfiniteQuery` or paged `useQuery` for any list that can grow. The recipe pool always can.
- Do not build client-side search/filter logic over in-memory lists.
- Never expand `limit` to work around missing server-side filtering.
- Scope query params tightly — send filters only when actually needed.

Decision gate:
1. Does an endpoint exist returning exactly this data, filtered/paginated server-side?
2. If yes → wire it in `*-api.ts` and `*-queries.ts`.
3. If no → **add it in `apps/api` first.** Never implement a client-side workaround.

---

## 5. React Best Practices

- Function components only.
- Prefer composition through `children`, slots, or focused subcomponents over prop drilling.
- State: `useState` for simple local values, `useReducer` for complex transitions, context for low-change globals (auth, theme, locale).
- **No manual memoization by default** — React 19 compiler handles it.
- Never use array indexes as keys; use stable identifiers.
- Prefer `startTransition` for non-urgent updates.
- Use component `key` intentionally when state should reset for a changed identity.
- Prefer granular error boundaries around independently failing sections.
- Prefer `use()` for context/async resources, `useActionState` for form submission, `useOptimistic` for optimistic UI.
- Pass `ref` as a prop; avoid `forwardRef`.

More than 3 `useState` calls in one component → extract a custom hook.
Imports from more than 5 feature directories → the file knows too much.

---

## 6. TypeScript Best Practices

- `strict: true` always.
- `interface` for extendable object shapes; `type` for unions, intersections, mapped types.
- Prefer discriminated unions over optional-property state bags.
- Avoid `any`; use `unknown` at boundaries and narrow with type guards.
- Exhaustive `never` checks in `switch` over discriminated unions.
- Prefer `satisfies`, `as const`, and utility types (`Pick`, `Omit`, `Partial`, `Record`).
- Annotate return types on all exported functions.
- Never use numeric enums.
- **Validate API responses at the boundary** — the API is a separate service, its shape is not guaranteed by the compiler.

---

## 7. Feature File Naming (Required)

```
src/features/{name}/api/{name}-api.ts       ← API calls
src/features/{name}/api/{name}-queries.ts   ← TanStack Query hooks
src/features/{name}/types/{name}-types.ts   ← interfaces/types
src/features/{name}/components/             ← feature components
```

Do not create parallel duplicates (`recipe-api.ts` and `recipe.api.ts`). Keep naming aligned with nearby files.

## 8. User-Generated Content Rules

- **Never auto-linkify user text.** The app renders no outbound links at all — there is no
  `source_url` field and no interstitial. Reversed 2026-08-04; see the PRODUCT.md decisions table.
- Every user-authored surface (recipe, comment) needs a reachable report action.
