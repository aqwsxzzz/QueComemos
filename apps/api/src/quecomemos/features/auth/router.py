"""Auth routes. Thin: validation, dependency injection, delegate to the service."""

from fastapi import APIRouter, status

from quecomemos.core.deps import DbSession
from quecomemos.features.auth import service
from quecomemos.features.auth.schemas import AuthSession, LoginRequest, RefreshRequest, TokenPair
from quecomemos.features.user.schemas import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthSession, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: DbSession) -> AuthSession:
    return await service.register(db, payload)


@router.post("/login", response_model=AuthSession)
async def login(payload: LoginRequest, db: DbSession) -> AuthSession:
    return await service.login(db, payload)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, db: DbSession) -> TokenPair:
    return await service.refresh(db, payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshRequest, db: DbSession) -> None:
    await service.logout(db, payload.refresh_token)
