"""Photo rows point at object storage. Bytes never live in Postgres."""

import uuid

from sqlalchemy import ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from quecomemos.core.db import Base
from quecomemos.core.mixins import TimestampMixin, UUIDMixin


class Photo(UUIDMixin, TimestampMixin, Base):
    """Attached to a recipe, and optionally to one of its steps.

    Process photos are the product differentiator, so a photo carries a nullable
    step_id rather than living in a separate table.
    """

    __tablename__ = "photo"

    recipe_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("recipe.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    step_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("recipe_step.id", ondelete="CASCADE"),
        index=True,
        default=None,
    )
    # Base storage key; variants are derived suffixes written by the pipeline.
    storage_key: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(200), default=None)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
