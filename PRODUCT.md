# Que Comemos? — Product Brief

> Living document. It answers "what are we building and why" so that any session can pick up
> context without re-deriving it from conversation. Update it when decisions change.

## The problem

Every day, twice a day, people stare into a kitchen and ask the same question: *what do I cook?*
Existing recipe sites answer with aspirational restaurant food — long ingredient lists, techniques
nobody has time for, photographed under studio lights.

## The product

A place where **home cooks share the food they actually cook**, with other home cooks.

Not Michelin. Not food styling. The pasta you make on a Tuesday because it works.
Tone is the product: unpretentious, real portions, real kitchens, photos taken with a phone.

## Platform

**Installable PWA.** Not a native app, not an app-store product.

Rationale: nothing here needs native capability — photo upload works fine from a browser. Going
PWA removes the Apple developer fee and review cycle, Google Play's closed-testing gate for new
accounts, and store UGC-compliance review. The app can be in front of real testers immediately.

Users are on phones. The web app must feel like it belongs there — that is a design obligation,
not a nice-to-have.

**Web/desktop is not a separate build**, but the responsive layout should not fight desktop use.
Recipe *authoring* is genuinely painful on a phone keyboard, and that is the one flow worth
making comfortable on a large screen.

## Language

Spanish-first. This matters beyond translation — see `docs/ingredients-model.md` for why regional
ingredient vocabulary (`palta`/`aguacate`, `porotos`/`frijoles`/`judías`) is a real data-model
concern and not a copy concern.

---

## Scope & Phasing

### Phase A — Recipes & community (build first)

- User accounts, normal email + password auth
- Recipe authoring: own instructions, own photos
- Photos of **the process**, not just the finished dish — this is a deliberate differentiator
- Optional external `source_url` when a recipe came from elsewhere
- Public searchable recipe pool with filtering
- Follow other cooks
- Favorites / saved recipes
- Comments and feedback on recipes
- A "help me out" affordance — asking about a specific step you don't understand
- Moderation primitives: report content, block a user, remove content + author

### Phase C — Meal planning (build second)

- Taste and diet preferences
- Weekly plan: what to cook each day, with alternatives ("here are 2–3 options")
- **Shopping list** — the union of ingredients across the planned week. This is the highest-value
  output of the phase and requires no pantry state at all.
- Plan is visible when the user opens the app. **No reminders, no push notifications.** Nobody
  needs to be alerted to eat; the value is that the plan is simply there.

### Phase B — Pantry / "virtual fridge" (deliberately NOT planned)

Originally scoped, now **cut**. Tracking real-world food stock is high-effort for the user and
needs a substitution-aware ingredient ontology to work at all. If it ever returns, the ingredient
model already supports it — but the working assumption is that it does not return.

Consequence: the app never tells a user "you're missing 2 ingredients." It doesn't know what
they have, and it doesn't try to.

---

## Decisions already made

| Decision | Rationale |
|---|---|
| PWA, not native | No native capability needed; removes store cost, review, and gating |
| No reminders/push | Nobody needs a notification to eat; plan-on-open is the whole value |
| Phase B cut | High user effort, hard data problem, unproven demand |
| Structured ingredients from migration #1 | Shopping list needs it; retrofitting is a rewrite. See `docs/ingredients-model.md` |
| Users never create canonical ingredients | They type free text; matching happens behind the scenes |
| External links allowed, but constrained | Stored `source_url`, domain allowlist, no auto-fetched previews, interstitial on tap. User text is never auto-linkified. |
| Moderation from day one | A public pool with photos needs it regardless of store rules |
| Deferred: private messages | Comments + the "help me out" flow probably cover the need. Revisit only if real usage shows otherwise. |

## Open questions

- Does "help me out" need to be a distinct entity, or is it a comment with a flag and a link to a step?
- Discovery: what ranks the pool? Recency is the honest v1 answer.
- Does a recipe need explicit servings/scaling in phase A, or is that a phase C concern?

## Non-goals

- Restaurant or professional cooking content
- Nutrition tracking / calorie counting
- Monetization (not now — do not design around it)
- Native mobile applications
