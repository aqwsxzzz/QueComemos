"""Comment business logic."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from quecomemos.core.errors import ForbiddenError, NotFoundError, ValidationError
from quecomemos.core.filters import apply_sort
from quecomemos.core.pagination import PageParams, paginate
from quecomemos.features.comment.models import Comment, CommentKind
from quecomemos.features.comment.schemas import CommentCreate, CommentFilters
from quecomemos.features.recipe.models import Recipe, RecipeStep
from quecomemos.features.report import blocks
from quecomemos.features.user.models import User

SORTABLE = {"created_at": Comment.created_at}
DEFAULT_SORT = "created_at"


async def _assert_step_belongs(db: AsyncSession, recipe_id: uuid.UUID, step_id: uuid.UUID) -> None:
    statement = select(RecipeStep.id).where(
        RecipeStep.id == step_id, RecipeStep.recipe_id == recipe_id
    )
    if (await db.execute(statement)).scalar_one_or_none() is None:
        raise ValidationError("Ese paso no pertenece a esta receta")


async def create(db: AsyncSession, author: User, recipe: Recipe, payload: CommentCreate) -> Comment:
    if payload.step_id is not None:
        await _assert_step_belongs(db, recipe.id, payload.step_id)
    if payload.kind is CommentKind.QUESTION and payload.step_id is None:
        raise ValidationError("Decinos sobre qué paso es la pregunta")
    if await blocks.is_blocked_between(db, author.id, recipe.author_id):
        raise ForbiddenError("No podés comentar en esta receta")

    comment = Comment(
        recipe_id=recipe.id,
        author_id=author.id,
        body=payload.body.strip(),
        kind=payload.kind,
        step_id=payload.step_id,
    )
    db.add(comment)
    await db.commit()
    return await get(db, comment.id)


async def get(db: AsyncSession, comment_id: uuid.UUID) -> Comment:
    statement = (
        select(Comment)
        .where(Comment.id == comment_id, Comment.removed_at.is_(None))
        .options(selectinload(Comment.author))
        .execution_options(populate_existing=True)
    )
    comment = (await db.execute(statement)).scalar_one_or_none()
    if comment is None:
        raise NotFoundError("Comentario no encontrado")
    return comment


async def list_for_recipe(
    db: AsyncSession,
    recipe_id: uuid.UUID,
    viewer: User | None,
    params: PageParams,
    filters: CommentFilters,
) -> tuple[list[Comment], int]:
    hidden = await blocks.blocked_user_ids(db, viewer.id if viewer else None)
    statement = (
        select(Comment)
        .where(Comment.recipe_id == recipe_id, Comment.removed_at.is_(None))
        .options(selectinload(Comment.author))
    )
    if hidden:
        statement = statement.where(Comment.author_id.not_in(hidden))
    if filters.kind is not None:
        statement = statement.where(Comment.kind == filters.kind)
    if filters.step_id is not None:
        statement = statement.where(Comment.step_id == filters.step_id)

    return await paginate(db, apply_sort(statement, SORTABLE, filters.sort, DEFAULT_SORT), params)


async def remove(db: AsyncSession, comment: Comment, user: User) -> None:
    """Authors delete their own; recipe owners and maintainers can moderate."""
    recipe_author_id = (
        await db.execute(select(Recipe.author_id).where(Recipe.id == comment.recipe_id))
    ).scalar_one()

    allowed = {comment.author_id, recipe_author_id}
    if user.id not in allowed and not user.is_maintainer:
        raise ForbiddenError("No podés borrar este comentario")

    comment.removed_at = datetime.now(UTC)
    await db.commit()
