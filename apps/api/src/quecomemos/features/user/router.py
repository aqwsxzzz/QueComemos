"""Account routes."""

import uuid

from fastapi import APIRouter

from quecomemos.core.deps import CurrentUser, DbSession
from quecomemos.features.user import service
from quecomemos.features.user.schemas import CookRead, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def read_me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/me", response_model=UserRead)
async def update_me(payload: UserUpdate, current_user: CurrentUser, db: DbSession) -> UserRead:
    user = await service.update(db, current_user, payload)
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=CookRead)
async def read_cook(user_id: uuid.UUID, db: DbSession) -> CookRead:
    """Public cook profile. Never exposes the email."""
    cook = await service.require_active(db, user_id)
    return CookRead.model_validate(cook)
