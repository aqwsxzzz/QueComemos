"""Shared FastAPI dependencies.

The recipe pool is publicly readable, so browse and search routes take the
optional variant — see apps/api/CLAUDE.md.
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from quecomemos.core.db import get_db
from quecomemos.core.errors import AuthenticationError
from quecomemos.core.security import token_subject
from quecomemos.features.user import service as user_service
from quecomemos.features.user.models import User

_required_scheme = HTTPBearer(auto_error=False)
_optional_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_required_scheme)],
) -> User:
    if credentials is None:
        raise AuthenticationError("Necesitás iniciar sesión")

    user_id = token_subject(credentials.credentials, "access")
    user = await user_service.get_active(db, user_id)
    if user is None:
        raise AuthenticationError("Sesión inválida o expirada")
    return user


async def get_current_user_optional(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_optional_scheme)],
) -> User | None:
    """Anonymous browsing is a feature, so a bad token here is simply anonymous."""
    if credentials is None:
        return None
    try:
        user_id = token_subject(credentials.credentials, "access")
    except AuthenticationError:
        return None
    return await user_service.get_active(db, user_id)


CurrentUser = Annotated[User, Depends(get_current_user)]
MaybeCurrentUser = Annotated[User | None, Depends(get_current_user_optional)]
