"""Recipe request/response shapes.

Recipes carry no outbound links at all: the product is what you cook, not a
pointer somewhere else. User prose is never scanned for links either.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from quecomemos.core.filters import FilterParams
from quecomemos.features.recipe.units import Unit
from quecomemos.features.user.schemas import CookRead


class RecipeIngredientWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_text: str = Field(min_length=1, max_length=255)


class RecipeIngredientRead(BaseModel):
    """`raw_text` is what renders. The rest exists for machine features."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    raw_text: str
    quantity: float | None
    unit: Unit | None
    ingredient_id: uuid.UUID | None
    position: int


class RecipeStepWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=2000)


class RecipeStepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    position: int
    text: str


class RecipeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=3, max_length=140)
    intro: str | None = Field(default=None, max_length=2000)
    servings: int | None = Field(default=None, ge=1, le=100)
    minutes: int | None = Field(default=None, ge=1, le=1440)
    ingredients: list[RecipeIngredientWrite] = Field(min_length=1, max_length=60)
    steps: list[RecipeStepWrite] = Field(min_length=1, max_length=40)


class RecipeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=3, max_length=140)
    intro: str | None = Field(default=None, max_length=2000)
    servings: int | None = Field(default=None, ge=1, le=100)
    minutes: int | None = Field(default=None, ge=1, le=1440)
    ingredients: list[RecipeIngredientWrite] | None = Field(default=None, max_length=60)
    steps: list[RecipeStepWrite] | None = Field(default=None, max_length=40)


class RecipeSummary(BaseModel):
    """What the pool lists. Deliberately without steps or ingredients."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    title: str
    intro: str | None
    servings: int | None
    minutes: int | None
    published_at: datetime | None
    author: CookRead
    # How many cooks saved this. Public on purpose — see the PRODUCT.md
    # decisions table. There is no separate "like": saving is the signal.
    favorites_count: int


class RecipeRead(RecipeSummary):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    ingredients: list[RecipeIngredientRead]
    steps: list[RecipeStepRead]


class RecipeFilters(FilterParams):
    """Typed list query params. `q` and `sort` come from FilterParams."""

    author_id: uuid.UUID | None = None
    ingredient_id: uuid.UUID | None = None
    max_minutes: int | None = Field(default=None, ge=1, le=1440)
