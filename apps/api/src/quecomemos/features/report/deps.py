"""Maintainer-only dependency."""

from typing import Annotated

from fastapi import Depends

from quecomemos.core.deps import CurrentUser
from quecomemos.core.errors import ForbiddenError
from quecomemos.features.user.models import User


async def require_maintainer(current_user: CurrentUser) -> User:
    if not current_user.is_maintainer:
        raise ForbiddenError("Necesitás permisos de moderación")
    return current_user


Maintainer = Annotated[User, Depends(require_maintainer)]
