"""Recipe, its ordered steps, and its ingredient rows."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from quecomemos.core.db import Base
from quecomemos.core.mixins import SoftRemovalMixin, TimestampMixin, UUIDMixin
from quecomemos.features.recipe.units import Unit
from quecomemos.features.user.models import User


class Recipe(UUIDMixin, TimestampMixin, SoftRemovalMixin, Base):
    __tablename__ = "recipe"
    __table_args__ = (Index("ix_recipe_pool", "published_at", "removed_at"),)

    author_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(140), nullable=False)
    intro: Mapped[str | None] = mapped_column(Text, default=None)
    servings: Mapped[int | None] = mapped_column(Integer, default=None)
    minutes: Mapped[int | None] = mapped_column(Integer, default=None)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    # Denormalized so the pool never joins `favorite` just to show a number —
    # that join fans out against the ingredient-filter subquery. Maintained by
    # the favorite service as an atomic SQL expression, never read-modify-write.
    # Not indexed yet: the index only earns its write cost once we sort by it.
    favorites_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )

    # lazy="raise" so a forgotten eager load fails loudly instead of emitting a
    # lazy query inside async code.
    author: Mapped[User] = relationship(lazy="raise")
    steps: Mapped[list[RecipeStep]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan", order_by="RecipeStep.position"
    )
    ingredients: Mapped[list[RecipeIngredient]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeIngredient.position",
    )


class RecipeStep(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "recipe_step"

    recipe_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("recipe.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    recipe: Mapped[Recipe] = relationship(back_populates="steps")


class RecipeIngredient(UUIDMixin, TimestampMixin, Base):
    """`raw_text` is always stored and is always what the user sees.

    `ingredient_id` is nullable and exists purely for machine features. A miss
    degrades aggregation; it never breaks the recipe.
    """

    __tablename__ = "recipe_ingredient"

    recipe_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("recipe.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    raw_text: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float | None] = mapped_column(Numeric(10, 3), default=None)
    unit: Mapped[Unit | None] = mapped_column(String(20), default=None)
    ingredient_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ingredient.id", ondelete="SET NULL"),
        index=True,
        default=None,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    recipe: Mapped[Recipe] = relationship(back_populates="ingredients")
