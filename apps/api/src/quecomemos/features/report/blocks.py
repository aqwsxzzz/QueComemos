"""Block lookups, kept separate so social features can filter without importing
the whole moderation surface.

Blocking is symmetric on read: if either side blocked the other, neither sees
the other's content. A one-way "I can still see you" would defeat the point.
"""

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from quecomemos.features.report.models import Block


async def blocked_user_ids(db: AsyncSession, user_id: uuid.UUID | None) -> set[uuid.UUID]:
    """Everyone this user blocked, plus everyone who blocked them."""
    if user_id is None:
        return set()

    statement = select(Block.blocker_id, Block.blocked_id).where(
        or_(Block.blocker_id == user_id, Block.blocked_id == user_id)
    )
    rows = await db.execute(statement)
    return {
        other
        for blocker_id, blocked_id in rows
        for other in (blocker_id, blocked_id)
        if other != user_id
    }


async def is_blocked_between(
    db: AsyncSession, first: uuid.UUID, second: uuid.UUID
) -> bool:
    statement = select(Block.id).where(
        or_(
            (Block.blocker_id == first) & (Block.blocked_id == second),
            (Block.blocker_id == second) & (Block.blocked_id == first),
        )
    )
    return (await db.execute(statement)).first() is not None
