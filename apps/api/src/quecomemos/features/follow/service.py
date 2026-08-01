"""Follow business logic."""

import uuid

from sqlalchemy import Select, delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from quecomemos.core.errors import ConflictError, ValidationError
from quecomemos.core.filters import apply_sort
from quecomemos.core.pagination import PageParams, paginate
from quecomemos.core.search import apply_search
from quecomemos.features.follow.models import Follow
from quecomemos.features.follow.schemas import CookFilters
from quecomemos.features.report import blocks
from quecomemos.features.user.models import User

SORTABLE = {"display_name": User.display_name, "created_at": User.created_at}
DEFAULT_SORT = "display_name"


async def follow(db: AsyncSession, follower: User, followee_id: uuid.UUID) -> None:
    if follower.id == followee_id:
        raise ValidationError("No podés seguirte a vos mismo")
    if await blocks.is_blocked_between(db, follower.id, followee_id):
        raise ValidationError("No podés seguir a esta persona")

    db.add(Follow(follower_id=follower.id, followee_id=followee_id))
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("Ya seguís a esta persona") from exc


async def unfollow(db: AsyncSession, follower: User, followee_id: uuid.UUID) -> None:
    """Idempotent: unfollowing someone you do not follow is not an error."""
    await db.execute(
        delete(Follow).where(Follow.follower_id == follower.id, Follow.followee_id == followee_id)
    )
    await db.commit()


async def is_following(db: AsyncSession, follower_id: uuid.UUID, followee_id: uuid.UUID) -> bool:
    statement = select(Follow.id).where(
        Follow.follower_id == follower_id, Follow.followee_id == followee_id
    )
    return (await db.execute(statement)).first() is not None


async def following_ids(db: AsyncSession, follower_id: uuid.UUID) -> set[uuid.UUID]:
    statement = select(Follow.followee_id).where(Follow.follower_id == follower_id)
    return set((await db.execute(statement)).scalars().all())


def _cooks_query(hidden: set[uuid.UUID]) -> Select[tuple[User]]:
    statement = select(User).where(User.removed_at.is_(None), User.is_active.is_(True))
    if hidden:
        statement = statement.where(User.id.not_in(hidden))
    return statement


async def list_following(
    db: AsyncSession, user: User, params: PageParams, filters: CookFilters
) -> tuple[list[User], int]:
    hidden = await blocks.blocked_user_ids(db, user.id)
    statement = _cooks_query(hidden).where(
        User.id.in_(select(Follow.followee_id).where(Follow.follower_id == user.id))
    )
    statement = apply_search(statement, (User.display_name,), filters.q)
    return await paginate(db, apply_sort(statement, SORTABLE, filters.sort, DEFAULT_SORT), params)


async def list_followers(
    db: AsyncSession, user: User, params: PageParams, filters: CookFilters
) -> tuple[list[User], int]:
    hidden = await blocks.blocked_user_ids(db, user.id)
    statement = _cooks_query(hidden).where(
        User.id.in_(select(Follow.follower_id).where(Follow.followee_id == user.id))
    )
    statement = apply_search(statement, (User.display_name,), filters.q)
    return await paginate(db, apply_sort(statement, SORTABLE, filters.sort, DEFAULT_SORT), params)
