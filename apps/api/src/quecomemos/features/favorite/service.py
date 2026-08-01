"""Favorite business logic."""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
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


async def add(db: AsyncSession, user: User, recipe_id: uuid.UUID) -> None:
    """Idempotent: saving something twice is the same as saving it once."""
    db.add(Favorite(user_id=user.id, recipe_id=recipe_id))
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()


async def remove(db: AsyncSession, user: User, recipe_id: uuid.UUID) -> None:
    await db.execute(
        delete(Favorite).where(Favorite.user_id == user.id, Favorite.recipe_id == recipe_id)
    )
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
