"""Moderation business logic: report, block, and take content down."""

import logging
import uuid

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from quecomemos.core.errors import ConflictError, NotFoundError, ValidationError
from quecomemos.core.filters import apply_sort
from quecomemos.core.pagination import PageParams, paginate
from quecomemos.features.comment.models import Comment
from quecomemos.features.follow.models import Follow
from quecomemos.features.recipe.models import Recipe
from quecomemos.features.report.models import Block, Report, ReportStatus, ReportTarget
from quecomemos.features.report.schemas import ReportCreate, ReportFilters
from quecomemos.features.user.models import User

logger = logging.getLogger(__name__)

SORTABLE = {"created_at": Report.created_at, "status": Report.status}
DEFAULT_SORT = "-created_at"

# The id columns rather than the model classes, so the lookup stays typed.
_TARGET_IDS = {
    ReportTarget.RECIPE: Recipe.id,
    ReportTarget.COMMENT: Comment.id,
    ReportTarget.USER: User.id,
}


async def _assert_target_exists(
    db: AsyncSession, target_type: ReportTarget, target_id: uuid.UUID
) -> None:
    column = _TARGET_IDS[target_type]
    if (await db.execute(select(column).where(column == target_id))).first() is None:
        raise NotFoundError("No encontramos eso que querés reportar")


async def create_report(db: AsyncSession, reporter: User, payload: ReportCreate) -> Report:
    await _assert_target_exists(db, payload.target_type, payload.target_id)
    if payload.target_type is ReportTarget.USER and payload.target_id == reporter.id:
        raise ValidationError("No podés reportarte a vos mismo")

    report = Report(
        reporter_id=reporter.id,
        target_type=payload.target_type,
        target_id=payload.target_id,
        reason=payload.reason,
        note=payload.note,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    logger.info("report filed: %s %s", payload.target_type, payload.target_id)
    return report


async def list_reports(
    db: AsyncSession, params: PageParams, filters: ReportFilters
) -> tuple[list[Report], int]:
    statement = select(Report)
    if filters.status is not None:
        statement = statement.where(Report.status == filters.status)
    if filters.target_type is not None:
        statement = statement.where(Report.target_type == filters.target_type)
    return await paginate(db, apply_sort(statement, SORTABLE, filters.sort, DEFAULT_SORT), params)


async def resolve_report(db: AsyncSession, report_id: uuid.UUID, status: ReportStatus) -> Report:
    report = (await db.execute(select(Report).where(Report.id == report_id))).scalar_one_or_none()
    if report is None:
        raise NotFoundError("Reporte no encontrado")
    report.status = status
    await db.commit()
    await db.refresh(report)
    return report


async def block(db: AsyncSession, blocker: User, blocked_id: uuid.UUID) -> Block:
    if blocker.id == blocked_id:
        raise ValidationError("No podés bloquearte a vos mismo")

    entry = Block(blocker_id=blocker.id, blocked_id=blocked_id)
    db.add(entry)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("Ya bloqueaste a esta persona") from exc

    # Blocking severs the follow edges in both directions: staying subscribed to
    # someone you blocked makes no sense.
    await db.execute(
        delete(Follow).where(
            ((Follow.follower_id == blocker.id) & (Follow.followee_id == blocked_id))
            | ((Follow.follower_id == blocked_id) & (Follow.followee_id == blocker.id))
        )
    )
    await db.commit()
    return await _get_with_cook(db, entry.id)


async def _get_with_cook(db: AsyncSession, block_id: uuid.UUID) -> Block:
    """Re-reads with the cook eager-loaded — `Block.blocked` is lazy="raise"."""
    statement = (
        select(Block).where(Block.id == block_id).options(selectinload(Block.blocked))
    )
    entry = (await db.execute(statement)).scalar_one_or_none()
    if entry is None:
        raise NotFoundError("Bloqueo no encontrado")
    return entry


async def unblock(db: AsyncSession, blocker: User, blocked_id: uuid.UUID) -> None:
    await db.execute(
        delete(Block).where(Block.blocker_id == blocker.id, Block.blocked_id == blocked_id)
    )
    await db.commit()


async def list_blocks(db: AsyncSession, blocker: User) -> list[Block]:
    statement = (
        select(Block)
        .where(Block.blocker_id == blocker.id)
        .options(selectinload(Block.blocked))
        .order_by(Block.created_at)
    )
    return list((await db.execute(statement)).scalars().all())
