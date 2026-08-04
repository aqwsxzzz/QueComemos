"""Favorite business logic."""

import uuid
from typing import Any, cast

from sqlalchemy import CursorResult, Result, delete, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from quecomemos.core.filters import apply_sort
from quecomemos.core.pagination import PageParams, paginate
from quecomemos.core.search import apply_search
from quecomemos.features.favorite.models import Favorite
from quecomemos.features.recipe.models import Recipe
from quecomemos.features.recipe.schemas import RecipeFilters
from quecomemos.features.recipe.service import DEFAULT_SORT, SEARCHABLE, SORTABLE
from quecomemos.features.report import blocks
from quecomemos.features.user.models import User


def _rowcount(result: Result[Any]) -> int:
    """`execute` is typed as returning Result; only CursorResult carries the
    affected-row count that DML actually produces."""
    return cast("CursorResult[Any]", result).rowcount


async def _shift_count(db: AsyncSession, recipe_id: uuid.UUID, delta: int) -> None:
    """Moves the denormalized counter by `delta` as one SQL expression.

    Read-modify-write in Python would lose an increment whenever two people
    save the same recipe at the same time.
    """
    await db.execute(
        update(Recipe)
        .where(Recipe.id == recipe_id)
        .values(favorites_count=Recipe.favorites_count + delta)
    )


async def add(db: AsyncSession, user: User, recipe_id: uuid.UUID) -> None:
    """Idempotent: saving something twice is the same as saving it once.

    ON CONFLICT DO NOTHING rather than catch-IntegrityError so the insert and
    the counter bump commit together — a rolled-back insert must not leave the
    count incremented.
    """
    statement = (
        pg_insert(Favorite)
        .values(user_id=user.id, recipe_id=recipe_id)
        .on_conflict_do_nothing(constraint="uq_favorite_pair")
    )
    if _rowcount(await db.execute(statement)) == 1:
        await _shift_count(db, recipe_id, 1)
    await db.commit()


async def remove(db: AsyncSession, user: User, recipe_id: uuid.UUID) -> None:
    """Only decrements when a row actually went away, so the count never
    drifts negative on a repeated unsave."""
    deleted = await db.execute(
        delete(Favorite).where(Favorite.user_id == user.id, Favorite.recipe_id == recipe_id)
    )
    if _rowcount(deleted) == 1:
        await _shift_count(db, recipe_id, -1)
    await db.commit()


async def is_favorited(db: AsyncSession, user_id: uuid.UUID, recipe_id: uuid.UUID) -> bool:
    statement = select(Favorite.id).where(
        Favorite.user_id == user_id, Favorite.recipe_id == recipe_id
    )
    return (await db.execute(statement)).first() is not None


async def list_for_user(
    db: AsyncSession, user: User, params: PageParams, filters: RecipeFilters
) -> tuple[list[Recipe], int]:
    hidden = await blocks.blocked_user_ids(db, user.id)
    statement = (
        select(Recipe)
        .where(
            Recipe.removed_at.is_(None),
            Recipe.published_at.is_not(None),
            Recipe.id.in_(select(Favorite.recipe_id).where(Favorite.user_id == user.id)),
        )
        .options(selectinload(Recipe.author))
    )
    if hidden:
        statement = statement.where(Recipe.author_id.not_in(hidden))

    statement = apply_search(statement, SEARCHABLE, filters.q)
    return await paginate(db, apply_sort(statement, SORTABLE, filters.sort, DEFAULT_SORT), params)
