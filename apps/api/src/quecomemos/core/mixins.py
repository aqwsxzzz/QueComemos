"""Column mixins shared by every model: identity, timestamps, soft removal."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class SoftRemovalMixin:
    """Removal policy for user-visible content — see apps/api/CLAUDE.md.

    Moderation must be able to take content down without destroying the audit
    trail, so user/recipe/comment are removed by stamping `removed_at`. Every
    read path filters on it; join rows (follow, favorite) hard-delete instead.
    """

    removed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    @property
    def is_removed(self) -> bool:
        return self.removed_at is not None
