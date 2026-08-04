"""Ingredient routes.

Public and read-only: the pool's ingredient filter needs to turn "pollo" into a
canonical id, and anonymous browsing of the pool is allowed.
"""

from typing import Annotated

from fastapi import APIRouter, Query

from quecomemos.core.deps import DbSession
from quecomemos.core.pagination import Page, build_page
from quecomemos.features.ingredient import service
from quecomemos.features.ingredient.schemas import IngredientFilters, IngredientRead

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get("", response_model=Page[IngredientRead])
async def list_ingredients(
    db: DbSession,
    filters: Annotated[IngredientFilters, Query()],
) -> Page[IngredientRead]:
    """Searchable by display name or regional alias, paginated server-side."""
    params = filters.page_params
    rows, total = await service.list_ingredients(db, params, filters)
    return build_page([IngredientRead.model_validate(row) for row in rows], total, params)
