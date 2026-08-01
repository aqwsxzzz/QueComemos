"""Session lifecycle: issue, rotate and revoke tokens.

Refresh tokens are persisted rather than trusted on signature alone, so that
removing or deactivating an account actually ends its live sessions.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy import update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from quecomemos.core.errors import AuthenticationError
from quecomemos.core.security import create_token, decode_token
from quecomemos.features.auth.schemas import AuthSession, LoginRequest, TokenPair
from quecomemos.features.user import service as user_service
from quecomemos.features.user.models import RefreshToken, User
from quecomemos.features.user.schemas import UserCreate, UserRead


async def _issue_tokens(db: AsyncSession, user: User) -> TokenPair:
    access_token, _ = create_token(user.id, "access")
    refresh_token, expires_at = create_token(user.id, "refresh")

    payload = decode_token(refresh_token, "refresh")
    db.add(RefreshToken(user_id=user.id, jti=str(payload["jti"]), expires_at=expires_at))
    await db.commit()

    return TokenPair(access_token=access_token, refresh_token=refresh_token)


async def register(db: AsyncSession, payload: UserCreate) -> AuthSession:
    user = await user_service.create(db, payload)
    tokens = await _issue_tokens(db, user)
    return AuthSession(user=UserRead.model_validate(user), tokens=tokens)


async def login(db: AsyncSession, payload: LoginRequest) -> AuthSession:
    user = await user_service.authenticate(db, payload.email, payload.password)
    if user is None:
        raise AuthenticationError("Email o contraseña incorrectos")
    tokens = await _issue_tokens(db, user)
    return AuthSession(user=UserRead.model_validate(user), tokens=tokens)


async def _consume_refresh_token(db: AsyncSession, token: str) -> tuple[User, RefreshToken]:
    payload = decode_token(token, "refresh")
    stored = (
        await db.execute(select(RefreshToken).where(RefreshToken.jti == str(payload["jti"])))
    ).scalar_one_or_none()

    if stored is None or stored.revoked_at is not None:
        raise AuthenticationError("Sesión inválida o expirada")
    if stored.expires_at <= datetime.now(UTC):
        raise AuthenticationError("Sesión inválida o expirada")

    user = await user_service.get_active(db, stored.user_id)
    if user is None:
        raise AuthenticationError("Sesión inválida o expirada")
    return user, stored


async def refresh(db: AsyncSession, token: str) -> TokenPair:
    """Rotates: the presented token is revoked as part of issuing the new pair."""
    user, stored = await _consume_refresh_token(db, token)
    stored.revoked_at = datetime.now(UTC)
    await db.flush()
    return await _issue_tokens(db, user)


async def logout(db: AsyncSession, token: str) -> None:
    """Best effort: an already-invalid token is not an error worth surfacing."""
    try:
        payload = decode_token(token, "refresh")
    except AuthenticationError:
        return
    await db.execute(
        sql_update(RefreshToken)
        .where(RefreshToken.jti == str(payload["jti"]), RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )
    await db.commit()


async def revoke_all_for_user(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Called by moderation when an account is removed or deactivated."""
    await db.execute(
        sql_update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )
    await db.commit()
