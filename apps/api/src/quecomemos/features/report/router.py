"""Moderation routes: reporting and blocking are public to any signed-in user;
takedowns are maintainer-only."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from quecomemos.core.deps import CurrentUser, DbSession
from quecomemos.core.pagination import Page, build_page
from quecomemos.features.report import service, takedown
from quecomemos.features.report.deps import Maintainer
from quecomemos.features.report.schemas import (
    BlockCreate,
    BlockRead,
    ReportCreate,
    ReportFilters,
    ReportRead,
    ReportResolve,
)

router = APIRouter(tags=["moderation"])


@router.post("/reports", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def create_report(
    payload: ReportCreate, current_user: CurrentUser, db: DbSession
) -> ReportRead:
    report = await service.create_report(db, current_user, payload)
    return ReportRead.model_validate(report)


@router.get("/reports", response_model=Page[ReportRead])
async def list_reports(
    _: Maintainer, db: DbSession, filters: Annotated[ReportFilters, Query()]
) -> Page[ReportRead]:
    params = filters.page_params
    rows, total = await service.list_reports(db, params, filters)
    return build_page([ReportRead.model_validate(row) for row in rows], total, params)


@router.patch("/reports/{report_id}", response_model=ReportRead)
async def resolve_report(
    report_id: uuid.UUID, payload: ReportResolve, _: Maintainer, db: DbSession
) -> ReportRead:
    report = await service.resolve_report(db, report_id, payload.status)
    return ReportRead.model_validate(report)


@router.post("/blocks", response_model=BlockRead, status_code=status.HTTP_201_CREATED)
async def create_block(payload: BlockCreate, current_user: CurrentUser, db: DbSession) -> BlockRead:
    entry = await service.block(db, current_user, payload.blocked_id)
    return BlockRead.model_validate(entry)


@router.delete("/blocks/{blocked_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_block(blocked_id: uuid.UUID, current_user: CurrentUser, db: DbSession) -> None:
    await service.unblock(db, current_user, blocked_id)


@router.get("/blocks", response_model=list[BlockRead])
async def list_blocks(current_user: CurrentUser, db: DbSession) -> list[BlockRead]:
    entries = await service.list_blocks(db, current_user)
    return [BlockRead.model_validate(entry) for entry in entries]


@router.delete("/moderation/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def take_down_recipe(recipe_id: uuid.UUID, _: Maintainer, db: DbSession) -> None:
    await takedown.remove_recipe(db, recipe_id)


@router.delete("/moderation/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def take_down_comment(comment_id: uuid.UUID, _: Maintainer, db: DbSession) -> None:
    await takedown.remove_comment(db, comment_id)


@router.delete("/moderation/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def take_down_author(user_id: uuid.UUID, _: Maintainer, db: DbSession) -> None:
    """Removes the account and everything it published, in one call."""
    await takedown.remove_author(db, user_id)
