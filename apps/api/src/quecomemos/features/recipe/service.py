"""Recipe business logic. The only layer here that touches the database."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from quecomemos.core.errors import NotFoundError
from quecomemos.core.filters import apply_sort
from quecomemos.core.pagination import PageParams, paginate
from quecomemos.core.search import apply_search
from quecomemos.features.ingredient import matcher
from quecomemos.features.recipe.models import Recipe, RecipeIngredient, RecipeStep
from quecomemos.features.recipe.parser import parse_ingredient_line
from quecomemos.features.recipe.schemas import RecipeCreate, RecipeFilters, RecipeUpdate
from quecomemos.features.user.models import User

SORTABLE = {
    "published_at": Recipe.published_at,
    "created_at": Recipe.created_at,
    "title": Recipe.title,
    "minutes": Recipe.minutes,
}
DEFAULT_SORT = "-published_at"
SEARCHABLE = (Recipe.title, Recipe.intro)


def _visible() -> Select[tuple[Recipe]]:
    """Removed recipes and unpublished drafts never appear in the pool."""
    return (
        select(Recipe)
        .where(Recipe.removed_at.is_(None), Recipe.published_at.is_not(None))
        .options(selectinload(Recipe.author))
    )


async def _build_ingredients(
    db: AsyncSession, recipe: Recipe, lines: list[str]
) -> list[RecipeIngredient]:
    rows: list[RecipeIngredient] = []
    for position, raw_text in enumerate(lines):
        parsed = parse_ingredient_line(raw_text)
        ingredient_id = await matcher.match(db, parsed.name)
        rows.append(
            RecipeIngredient(
                recipe_id=recipe.id,
                raw_text=raw_text,
                quantity=parsed.quantity,
                unit=parsed.unit,
                ingredient_id=ingredient_id,
                position=position,
            )
        )
    return rows


async def get_visible(db: AsyncSession, recipe_id: uuid.UUID) -> Recipe:
    statement = (
        _visible()
        .where(Recipe.id == recipe_id)
        .options(selectinload(Recipe.ingredients), selectinload(Recipe.steps))
    )
    recipe = (await db.execute(statement)).scalar_one_or_none()
    if recipe is None:
        raise NotFoundError("Receta no encontrada")
    return recipe


async def get_for_author(db: AsyncSession, recipe_id: uuid.UUID) -> Recipe:
    """Includes drafts, so an author can load their own unpublished recipe.

    `populate_existing` because this is the read-after-write path: sessions use
    `expire_on_commit=False`, so an already-loaded collection would otherwise be
    returned stale after the children were replaced.
    """
    statement = (
        select(Recipe)
        .where(Recipe.id == recipe_id, Recipe.removed_at.is_(None))
        .options(
            selectinload(Recipe.author),
            selectinload(Recipe.ingredients),
            selectinload(Recipe.steps),
        )
        .execution_options(populate_existing=True)
    )
    recipe = (await db.execute(statement)).scalar_one_or_none()
    if recipe is None:
        raise NotFoundError("Receta no encontrada")
    return recipe


async def create(db: AsyncSession, author: User, payload: RecipeCreate) -> Recipe:
    recipe = Recipe(
        author_id=author.id,
        title=payload.title.strip(),
        intro=payload.intro,
        servings=payload.servings,
        minutes=payload.minutes,
        published_at=datetime.now(UTC),
    )
    db.add(recipe)
    await db.flush()

    db.add_all(await _build_ingredients(db, recipe, [i.raw_text for i in payload.ingredients]))
    db.add_all(
        RecipeStep(recipe_id=recipe.id, position=position, text=step.text)
        for position, step in enumerate(payload.steps)
    )
    await db.commit()
    return await get_for_author(db, recipe.id)


async def _replace_children(db: AsyncSession, recipe: Recipe, payload: RecipeUpdate) -> None:
    if payload.ingredients is not None:
        recipe.ingredients.clear()
        await db.flush()
        db.add_all(await _build_ingredients(db, recipe, [i.raw_text for i in payload.ingredients]))
    if payload.steps is not None:
        recipe.steps.clear()
        await db.flush()
        db.add_all(
            RecipeStep(recipe_id=recipe.id, position=position, text=step.text)
            for position, step in enumerate(payload.steps)
        )


async def update(db: AsyncSession, recipe: Recipe, payload: RecipeUpdate) -> Recipe:
    fields = payload.model_dump(exclude_unset=True, exclude={"ingredients", "steps"})
    for field, value in fields.items():
        setattr(recipe, field, value)

    await _replace_children(db, recipe, payload)
    await db.commit()
    return await get_for_author(db, recipe.id)


async def remove(db: AsyncSession, recipe: Recipe) -> None:
    """Soft delete: moderation needs the row to survive its own takedown."""
    recipe.removed_at = datetime.now(UTC)
    await db.commit()


def _apply_filters(
    statement: Select[tuple[Recipe]], filters: RecipeFilters
) -> Select[tuple[Recipe]]:
    if filters.author_id is not None:
        statement = statement.where(Recipe.author_id == filters.author_id)
    if filters.max_minutes is not None:
        statement = statement.where(Recipe.minutes <= filters.max_minutes)
    if filters.ingredient_id is not None:
        statement = statement.where(
            Recipe.id.in_(
                select(RecipeIngredient.recipe_id).where(
                    RecipeIngredient.ingredient_id == filters.ingredient_id
                )
            )
        )
    return statement


async def list_pool(
    db: AsyncSession, params: PageParams, filters: RecipeFilters
) -> tuple[list[Recipe], int]:
    statement = apply_search(_apply_filters(_visible(), filters), SEARCHABLE, filters.q)
    statement = apply_sort(statement, SORTABLE, filters.sort, DEFAULT_SORT)
    return await paginate(db, statement, params)
