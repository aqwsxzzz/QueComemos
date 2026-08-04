"""Hard removal of content and authors.

The removal policy from apps/api/CLAUDE.md, applied in one place: user, recipe
and comment are soft-deleted by stamping `removed_at`, every read path filters
on it, and photo objects are purged from storage because bytes should not
outlive the row that pointed at them.
"""

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy import update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from quecomemos.core.errors import NotFoundError
from quecomemos.features.auth import service as auth_service
from quecomemos.features.comment.models import Comment
from quecomemos.features.photo import service as photo_service
from quecomemos.features.recipe.models import Recipe
from quecomemos.features.user.models import User

logger = logging.getLogger(__name__)


async def _require_present(
    db: AsyncSession,
    column: InstrumentedAttribute[uuid.UUID],
    model_id: uuid.UUID,
    label: str,
) -> None:
    if (await db.execute(select(column).where(column == model_id))).first() is None:
        raise NotFoundError(label)


async def remove_recipe(db: AsyncSession, recipe_id: uuid.UUID) -> None:
    """Takes a recipe down along with its comments and stored photos."""
    await _require_present(db, Recipe.id, recipe_id, "Receta no encontrada")

    now = datetime.now(UTC)
    await db.execute(
        sql_update(Recipe)
        .where(Recipe.id == recipe_id, Recipe.removed_at.is_(None))
        .values(removed_at=now)
    )
    await db.execute(
        sql_update(Comment)
        .where(Comment.recipe_id == recipe_id, Comment.removed_at.is_(None))
        .values(removed_at=now)
    )
    await db.commit()
    await photo_service.purge_for_recipe(db, recipe_id)
    logger.info("recipe removed by moderation: %s", recipe_id)


async def remove_author(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Removes an account and everything it published, then kills its sessions."""
    await _require_present(db, User.id, user_id, "Usuario no encontrado")

    now = datetime.now(UTC)
    await db.execute(
        sql_update(User).where(User.id == user_id).values(removed_at=now, is_active=False)
    )
    recipe_ids = list(
        (await db.execute(select(Recipe.id).where(Recipe.author_id == user_id))).scalars().all()
    )
    await db.execute(
        sql_update(Recipe)
        .where(Recipe.author_id == user_id, Recipe.removed_at.is_(None))
        .values(removed_at=now)
    )
    await db.execute(
        sql_update(Comment)
        .where(Comment.author_id == user_id, Comment.removed_at.is_(None))
        .values(removed_at=now)
    )
    await db.commit()

    for recipe_id in recipe_ids:
        await photo_service.purge_for_recipe(db, recipe_id)

    # A ban that leaves live sessions working is not a ban.
    await auth_service.revoke_all_for_user(db, user_id)
    logger.info("author removed by moderation: %s (%s recipes)", user_id, len(recipe_ids))


async def remove_comment(db: AsyncSession, comment_id: uuid.UUID) -> None:
    await _require_present(db, Comment.id, comment_id, "Comentario no encontrado")

    await db.execute(
        sql_update(Comment)
        .where(Comment.id == comment_id, Comment.removed_at.is_(None))
        .values(removed_at=datetime.now(UTC))
    )
    await db.commit()
