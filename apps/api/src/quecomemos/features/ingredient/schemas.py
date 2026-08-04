"""Ingredient request/response shapes.

Read-only on purpose: the taxonomy is curated by the maintainer, so there is no
Create or Update schema here. See docs/ingredients-model.md.
"""

import uuid

from pydantic import BaseModel, ConfigDict

from quecomemos.core.filters import FilterParams


class IngredientRead(BaseModel):
    """A canonical ingredient as the filter UI sees it.

    `slug` stays internal: it is a matching key, not something to render.
    """

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    name: str
    category: str | None


class IngredientFilters(FilterParams):
    """`q` matches the display name and every regional alias."""

    category: str | None = None
