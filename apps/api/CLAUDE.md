# CLAUDE.md — apps/api

Read `../../CLAUDE.md` (root) and `../../PRODUCT.md` first. This file owns backend rules only.

```yaml
project:
  name: quecomemos-api
  type: REST API
  domain: home-cook recipe sharing (see ../../PRODUCT.md)
  language: python 3.14
  framework: fastapi
  orm: sqlalchemy 2.0 async
  migrations: alembic
  validation: pydantic v2
  package_manager: uv
  database: postgresql 16
  entry: src/quecomemos/main.py
  src_dir: src/
  status: greenfield — phase A (recipes & community) not yet started

scripts:
  dev: uv run uvicorn quecomemos.main:app --reload --host 0.0.0.0
  start: uv run uvicorn quecomemos.main:app --host 0.0.0.0
  test: uv run pytest
  lint: uv run ruff check
  format: uv run ruff format
  typecheck: uv run mypy src
  migrate: uv run alembic upgrade head
  migrate_new: uv run alembic revision --autogenerate -m "<msg>"
  migrate_down: uv run alembic downgrade -1
  seed: uv run python -m quecomemos.scripts.seed

formatting:
  tool: ruff (format + check)
  line_length: 100
  quotes: double
  indent: 4 spaces
  import_sort: ruff (isort-compatible)

naming:
  files: snake_case
  modules: snake_case
  variables: snake_case
  functions: snake_case
  classes: PascalCase
  constants: UPPER_SNAKE_CASE
  db_columns: snake_case
  db_tables: snake_case (singular, e.g. recipe, ingredient)

python:
  target: "3.14"
  type_hints: required on all function signatures
  strict: mypy --strict (no implicit Any, no untyped defs)
  async: default for I/O; sync only for pure helpers
  no_star_imports: true

architecture:
  pattern: feature-folders (everything per-feature close together)
  api_prefix: /api/v1
  app_factory: src/quecomemos/main.py

project_layout:
  root: src/quecomemos/
  core:
    location: src/quecomemos/core/
    files:
      - config.py        # pydantic-settings, env vars
      - db.py            # async engine, session, get_db dep
      - security.py      # JWT encode/decode, password hashing
      - deps.py          # get_current_user, pagination
      - errors.py        # domain exceptions + FastAPI exception handlers
      - pagination.py    # Page, PageParams, paginate()
      - filters.py       # FilterParams base, apply_filters()
      - search.py        # search helper (ILIKE over configured columns)
      - text.py          # normalization: lowercase, strip accents, singularize
  features:
    location: src/quecomemos/features/{name}/
    files:
      - router.py        # APIRouter, thin — validation + dep injection
      - models.py        # SQLAlchemy models
      - schemas.py       # Pydantic request/response schemas
      - service.py       # business logic, only layer touching DB
      - deps.py          # feature-local dependencies (optional)
      - guards.py        # cross-entity assertions (optional)
  rules:
    - singular feature name (recipe, not recipes)
    - service is the only layer touching the database
    - routers never import models directly — go through service
    - schemas.py owns serialization; service returns models, router returns schemas
    - cross-feature calls go service → service, never model imports

planned_features:
  phase_a: [user, auth, recipe, ingredient, photo, follow, favorite, comment, report]
  phase_c: [preference, meal_plan, shopping_list]
  cut: [pantry]

ingredients:
  rule: canonical entity + alias table + nullable FK on recipe_ingredient
  raw_text: always stored, always displayed, never mutated
  users_never_create_canonical_ingredients: true
  unmatched: ingredient_id stays NULL, normalized form goes to a review queue
  spec: ../../docs/ingredients-model.md
  note: this must exist in migration #1 — retrofitting is a rewrite

list_endpoints:
  mandatory_from_day_0: true
  every_list_endpoint_supports:
    - pagination: offset/limit + total count, standard response envelope
    - search: q param, ILIKE over feature-declared searchable columns
    - filtering: typed query params per feature, declared in schemas.py
    - sorting: sort param, whitelist of allowed columns per feature
  response_envelope:
    data: list[Schema]
    meta: { page: int, page_size: int, total: int, has_next: bool }
  implementation:
    - core/pagination.py owns PageParams (page, page_size) + Page[T] generic
    - core/filters.py owns FilterParams base; each feature extends
    - core/search.py owns search(query, columns, term) helper
    - service accepts (params, filters, search_term, sort) — returns (rows, total)
    - router wraps into Page[Schema] response model
  list_endpoint_shape: |
    async def list_items(
        params: PageParams = Depends(),
        filters: ItemFilters = Depends(),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> Page[ItemRead]: ...

schemas:
  library: pydantic v2
  patterns:
    - {Name}Create — POST body
    - {Name}Update — PATCH body (all fields optional)
    - {Name}Read — response model (exposes fields, hides secrets)
    - {Name}Filters — list query params (extends FilterParams)
  config:
    from_attributes: true
    extra: forbid

responses:
  success: return Pydantic schema directly; FastAPI serializes
  error: raise domain exception (AppError subclass); handler formats envelope
  envelope:
    success: { data, meta? }
    error: { detail, code, errors[]? }

auth:
  method: JWT bearer tokens
  header: "Authorization: Bearer <token>"
  access_token_ttl: 15m
  refresh_token_ttl: 7d
  password_hash: bcrypt
  deps: get_current_user (required), get_current_user_optional (public browsing)
  note: the recipe pool is publicly readable — use the optional dep on browse/search routes

user_generated_content:
  outbound_links:
    - none: recipes carry no URL field, and user text is never parsed for links
    - reversed 2026-08-04; see the PRODUCT.md decisions table
  moderation:
    - report, block, and hard-remove (content + author) exist from phase A
    - removal must cascade or soft-delete consistently — decide once, apply everywhere
  photos:
    - object storage + resize pipeline, not DB blobs
    - strip EXIF (location data) on upload

database:
  engine: asyncpg via sqlalchemy.ext.asyncio
  session: scoped per request via FastAPI dep
  migrations:
    tool: alembic
    location: migrations/versions/
    must_have: up and down functions
  pool: { size: 5, max_overflow: 10, pool_pre_ping: true }
  query_rules:
    - no raw SQL unless justified (use select(), insert(), update())
    - prefer select() with explicit columns
    - eager-load relationships with selectinload / joinedload — never lazy in async
    - use SAVEPOINT for nested transactions
  errors:
    - catch IntegrityError in service, re-raise as ConflictError
    - catch NoResultFound in service, re-raise as NotFoundError

logging:
  use: logging.getLogger(__name__)
  never: print()

cors:
  origins: ALLOWED_ORIGINS env var, comma separated
  credentials: true
  methods: [GET, POST, PUT, PATCH, DELETE, OPTIONS]

test_framework: pytest + pytest-asyncio + httpx.AsyncClient
test_factories: polyfactory
test_rules:
  - integration tests use real postgres
  - no mocking the DB — mock only external HTTP
  - Arrange-Act-Assert structure
  - one assertion per concept

docker:
  rule: ALWAYS run commands inside Docker containers, never on host
  app_container: app
  dev: docker compose up
  exec_pattern: docker compose exec app <command>
  examples:
    - docker compose exec app uv run pytest
    - docker compose exec app uv run alembic upgrade head
```

## File Size Enforcement

**Never write a file longer than 200 lines.** If a file would exceed 200 lines, split it into smaller modules before writing.
