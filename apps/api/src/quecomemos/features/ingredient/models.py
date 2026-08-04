"""Canonical ingredient taxonomy — curated by the maintainer, never by users.

See docs/ingredients-model.md. Users type free text; matching happens behind the
scenes and a miss is recorded here rather than pushed back at the author.
"""

import uuid

from sqlalchemy import ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from quecomemos.core.db import Base
from quecomemos.core.mixins import TimestampMixin, UUIDMixin


class Ingredient(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ingredient"

    # Display form, e.g. "tomate". Shown only in maintainer tooling — recipes
    # always render their own raw_text.
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    # Normalized matching key, e.g. "tomate". Unique so seeding is idempotent.
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(40), default=None)

    aliases: Mapped[list[IngredientAlias]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )


class IngredientAlias(UUIDMixin, TimestampMixin, Base):
    """Many normalized forms → one canonical ingredient.

    This is where regional vocabulary lives: palta/aguacate, porotos/frijoles/
    judías, choclo/maíz/elote, frutilla/fresa.
    """

    __tablename__ = "ingredient_alias"

    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ingredient.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    # Already run through core.text.normalize_for_match at write time.
    normalized: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)

    ingredient: Mapped[Ingredient] = relationship(back_populates="aliases")


class IngredientReviewQueue(UUIDMixin, TimestampMixin, Base):
    """Normalized forms that matched nothing.

    The maintainer clears this by adding aliases. Nothing here blocks a user:
    the recipe already saved fine with a NULL ingredient_id.
    """

    __tablename__ = "ingredient_review_queue"

    normalized: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    sample_raw_text: Mapped[str] = mapped_column(String(255), nullable=False)
    hit_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    resolved_ingredient_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("ingredient.id", ondelete="SET NULL"), default=None
    )
