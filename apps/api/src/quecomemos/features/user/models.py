"""User accounts and persisted refresh tokens."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from quecomemos.core.db import Base
from quecomemos.core.mixins import SoftRemovalMixin, TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, SoftRemovalMixin, Base):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(60), nullable=False)
    bio: Mapped[str | None] = mapped_column(String(280), default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Maintainer of the ingredient taxonomy and the moderation queue. Set by hand.
    is_maintainer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class RefreshToken(UUIDMixin, TimestampMixin, Base):
    """Stored so that a ban or an account removal actually kills live sessions."""

    __tablename__ = "refresh_token"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
