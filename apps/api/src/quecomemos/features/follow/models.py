"""Follow edges. A join row, so removal is a hard delete."""

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from quecomemos.core.db import Base
from quecomemos.core.mixins import TimestampMixin, UUIDMixin


class Follow(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "follow"
    __table_args__ = (
        UniqueConstraint("follower_id", "followee_id", name="uq_follow_pair"),
        CheckConstraint("follower_id <> followee_id", name="ck_follow_not_self"),
    )

    follower_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    followee_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
