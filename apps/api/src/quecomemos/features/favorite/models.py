"""Favorite edges. A join row, so removal is a hard delete."""

import uuid

from sqlalchemy import ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from quecomemos.core.db import Base
from quecomemos.core.mixins import TimestampMixin, UUIDMixin


class Favorite(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "favorite"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_favorite_pair"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    recipe_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("recipe.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
