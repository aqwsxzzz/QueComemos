"""Account business logic. The only layer here that touches the database."""

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from quecomemos.core.errors import ConflictError, NotFoundError
from quecomemos.core.security import hash_password, verify_password
from quecomemos.features.user.models import User
from quecomemos.features.user.schemas import UserCreate, UserUpdate

# Burned when no account matches, so a missing email and a wrong password take
# the same time and the endpoint cannot be used to enumerate accounts.
_DUMMY_HASH = hash_password("account-enumeration-guard")


def _normalize_email(email: str) -> str:
    return email.strip().lower()


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == _normalize_email(email))
    return (await db.execute(statement)).scalar_one_or_none()


async def get_active(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Active means: exists, not removed by moderation, not deactivated."""
    statement = select(User).where(
        User.id == user_id, User.removed_at.is_(None), User.is_active.is_(True)
    )
    return (await db.execute(statement)).scalar_one_or_none()


async def require_active(db: AsyncSession, user_id: uuid.UUID) -> User:
    user = await get_active(db, user_id)
    if user is None:
        raise NotFoundError("Usuario no encontrado")
    return user


async def create(db: AsyncSession, payload: UserCreate) -> User:
    user = User(
        email=_normalize_email(payload.email),
        password_hash=hash_password(payload.password),
        display_name=payload.display_name.strip(),
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("Ya existe una cuenta con ese email") from exc
    await db.refresh(user)
    return user


async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
    """Returns None for every failure mode, so callers cannot leak which one."""
    user = await get_by_email(db, email)
    if user is None or user.removed_at is not None or not user.is_active:
        verify_password(password, _DUMMY_HASH)
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def update(db: AsyncSession, user: User, payload: UserUpdate) -> User:
    if payload.display_name is not None:
        user.display_name = payload.display_name.strip()
    if payload.bio is not None:
        user.bio = payload.bio.strip() or None
    await db.commit()
    await db.refresh(user)
    return user
