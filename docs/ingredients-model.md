# Ingredient Model — canonical entities with free-text fallback

## The problem

Recipe ingredients must be **displayable exactly as the author wrote them** and **aggregatable by
the machine** (shopping lists, "recipes with pollo", diet filtering). Those two goals pull in
opposite directions:

- Pure free text → the shopping list can never merge "2 tomates" from one recipe with
  "3 tomates" from another. Search by ingredient never works properly.
- Pure canonical entities → users are forced into data entry, authoring becomes a chore,
  and the taxonomy has to be complete on day one. It never is.

## The design

**Users never create canonical ingredients.** They type free text, as they always would.
Matching happens in the background.

### Tables

**`ingredient`** — canonical, curated by the maintainer, never by users.
Seeded with ~400 common ingredients. `tomate`, `cebolla`, `pollo`, `harina`.

**`ingredient_alias`** — many aliases → one canonical ingredient.
`tomates`, `jitomate`, `tomate perita` → `tomate`.
Carries the regional vocabulary: `palta`/`aguacate`, `porotos`/`frijoles`/`judías`,
`choclo`/`maíz`/`elote`, `frutilla`/`fresa`.

**`recipe_ingredient`** — the join, per recipe:

| column | note |
|---|---|
| `recipe_id` | FK |
| `raw_text` | **always stored, always what gets displayed** |
| `quantity` | nullable numeric |
| `unit` | nullable, canonical unit enum |
| `ingredient_id` | **nullable** FK to `ingredient` |
| `position` | display order |

### The load-bearing rule

> `raw_text` is always stored and is always what the user sees.
> `ingredient_id` exists purely for machine features.

That nullable FK is what makes this safe. If someone writes
*"tomate cherry orgánico del huerto de mi abuela"* and nothing matches, the recipe still renders
perfectly — it simply doesn't participate in aggregation.

**Nothing breaks. A feature degrades.** That is the whole difference between this design and an
ontology project.

## Matching

On write, normalize **for matching only** — never mutate `raw_text`:

1. lowercase
2. strip accents
3. singularize
4. look up the normalized form in `ingredient_alias`

Match → set `ingredient_id`. No match → leave it `NULL` and record the normalized form in a
review queue.

The maintainer clears that queue periodically by adding aliases. The system gets smarter over
time and **never blocks a user** while doing so.

## Units

Same treatment, smaller scale. A canonical unit enum (`g`, `kg`, `ml`, `l`, `unidad`,
`cucharada`, `cucharadita`, `taza`, `pizca`, …) plus a parser for the quantity string.

Unparseable → keep the raw string, skip aggregation for that row. Same degrade-don't-break rule.

## Why this must exist in migration #1

The Phase C shopping list cannot merge quantities without it, and ingredient search/filtering in
Phase A is weak without it. Adding structured ingredients after recipes exist means backfilling
every recipe by parsing text — that's a rewrite, not a migration.

**Cost of doing it now:** two extra tables, one nullable FK, one seed script.

## What this is not

- Not a nutrition database
- Not a substitution engine
- Not user-editable taxonomy
- Not a dependency for Phase B (which is cut) — it earns its place through the shopping list alone
