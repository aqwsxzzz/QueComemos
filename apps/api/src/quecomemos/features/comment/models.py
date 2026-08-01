"""Comments, including the "help me out" affordance.

A question is not a separate entity: it is a comment with kind='question' and a
step_id, so it inherits the same moderation path and the same read filters.
"""

import uuid
from enum import StrEnum

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from quecomemos.core.db import Base
from quecomemos.core.mixins import SoftRemovalMixin, TimestampMixin, UUIDMixin


class CommentKind(StrEnum):
    COMMENT = "comment"
    QUESTION = "question"


class Comment(UUIDMixin, TimestampMixin, SoftRemovalMixin, Base):
    __tablename__ = "comment"

    recipe_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("recipe.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[CommentKind] = mapped_column(
        String(20), default=CommentKind.COMMENT, nullable=False
    )
    # Set when the comment asks about one specific step.
    step_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("recipe_step.id", ondelete="CASCADE"), default=None
    )
