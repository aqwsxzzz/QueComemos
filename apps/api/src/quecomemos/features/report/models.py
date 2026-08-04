"""Moderation primitives: report content, block a user.

Present from phase A. A public pool with photos needs them regardless of any
store rule — see PRODUCT.md.
"""

import uuid
from enum import StrEnum

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from quecomemos.core.db import Base
from quecomemos.core.mixins import TimestampMixin, UUIDMixin
from quecomemos.features.user.models import User


class ReportTarget(StrEnum):
    RECIPE = "recipe"
    COMMENT = "comment"
    USER = "user"


class ReportStatus(StrEnum):
    OPEN = "open"
    REVIEWED = "reviewed"
    ACTIONED = "actioned"
    DISMISSED = "dismissed"


class ReportReason(StrEnum):
    SPAM = "spam"
    ABUSE = "abuse"
    SEXUAL = "sexual"
    NOT_A_RECIPE = "not_a_recipe"
    OTHER = "other"


class Report(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "report"

    reporter_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # Loose reference on purpose: one queue across recipe, comment and user.
    target_type: Mapped[ReportTarget] = mapped_column(String(20), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True, nullable=False)
    reason: Mapped[ReportReason] = mapped_column(String(20), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, default=None)
    status: Mapped[ReportStatus] = mapped_column(
        String(20), default=ReportStatus.OPEN, index=True, nullable=False
    )


class Block(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "block"
    __table_args__ = (UniqueConstraint("blocker_id", "blocked_id", name="uq_block_pair"),)

    blocker_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    blocked_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # The blocked-users screen needs a name to show. Without this the client
    # would fetch each cook separately — one request per row.
    # lazy="raise" so a forgotten eager load fails loudly in async code.
    blocked: Mapped[User] = relationship(foreign_keys=[blocked_id], lazy="raise")
