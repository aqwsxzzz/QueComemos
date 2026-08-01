"""Follow routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from quecomemos.core.deps import CurrentUser, DbSession
from quecomemos.core.pagination import Page, build_page
from quecomemos.features.follow import service
from quecomemos.features.follow.schemas import CookFilters, FollowStatus
from quecomemos.features.user import service as user_service
from quecomemos.features.user.schemas import CookRead

router = APIRouter(tags=["follows"])


@router.put("/cooks/{cook_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def follow_cook(cook_id: uuid.UUID, current_user: CurrentUser, db: DbSession) -> None:
    await service.follow(db, current_user, cook_id)


@router.delete("/cooks/{cook_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_cook(cook_id: uuid.UUID, current_user: CurrentUser, db: DbSession) -> None:
    await service.unfollow(db, current_user, cook_id)


@router.get("/cooks/{cook_id}/follow", response_model=FollowStatus)
async def read_follow_status(
    cook_id: uuid.UUID, current_user: CurrentUser, db: DbSession
) -> FollowStatus:
    cook = await user_service.require_active(db, cook_id)
    following = await service.is_following(db, current_user.id, cook_id)
    return FollowStatus(**CookRead.model_validate(cook).model_dump(), is_followed=following)


@router.get("/me/following", response_model=Page[CookRead])
async def list_following(
    current_user: CurrentUser, db: DbSession, filters: Annotated[CookFilters, Query()]
) -> Page[CookRead]:
    params = filters.page_params
    rows, total = await service.list_following(db, current_user, params, filters)
    return build_page([CookRead.model_validate(row) for row in rows], total, params)


@router.get("/me/followers", response_model=Page[CookRead])
async def list_followers(
    current_user: CurrentUser, db: DbSession, filters: Annotated[CookFilters, Query()]
) -> Page[CookRead]:
    params = filters.page_params
    rows, total = await service.list_followers(db, current_user, params, filters)
    return build_page([CookRead.model_validate(row) for row in rows], total, params)
