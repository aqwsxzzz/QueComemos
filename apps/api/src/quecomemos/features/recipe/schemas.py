"""Recipe request/response shapes.

`source_url` is validated against a host allowlist here, at the boundary, and is
never fetched server-side. User prose is never scanned for links.
"""

import uuid
from datetime import datetime
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator

from quecomemos.core.config import get_settings
from quecomemos.core.filters import FilterParams
from quecomemos.features.recipe.units import Unit
from quecomemos.features.user.schemas import CookRead


def _validate_source_url(value: str | None) -> str | None:
    if value is None:
        return None

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("El enlace debe empezar con http:// o https://")

    host = parsed.hostname.lower().removeprefix("www.")
    allowed = get_settings().allowed_source_hosts
    if host not in allowed and not any(host.endswith(f".{entry}") for entry in allowed):
        raise ValueError(f"No aceptamos enlaces de {host} todavía")
    return value


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
    source_url: str | None = Field(default=None, max_length=500)
    ingredients: list[RecipeIngredientWrite] = Field(min_length=1, max_length=60)
    steps: list[RecipeStepWrite] = Field(min_length=1, max_length=40)

    _check_source_url = field_validator("source_url")(_validate_source_url)


class RecipeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=3, max_length=140)
    intro: str | None = Field(default=None, max_length=2000)
    servings: int | None = Field(default=None, ge=1, le=100)
    minutes: int | None = Field(default=None, ge=1, le=1440)
    source_url: str | None = Field(default=None, max_length=500)
    ingredients: list[RecipeIngredientWrite] | None = Field(default=None, max_length=60)
    steps: list[RecipeStepWrite] | None = Field(default=None, max_length=40)

    _check_source_url = field_validator("source_url")(_validate_source_url)


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


class RecipeRead(RecipeSummary):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    source_url: str | None
    ingredients: list[RecipeIngredientRead]
    steps: list[RecipeStepRead]


class RecipeFilters(FilterParams):
    """Typed list query params. `q` and `sort` come from FilterParams."""

    author_id: uuid.UUID | None = None
    ingredient_id: uuid.UUID | None = None
    max_minutes: int | None = Field(default=None, ge=1, le=1440)
