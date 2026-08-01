"""Favorite routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from quecomemos.core.deps import CurrentUser, DbSession
from quecomemos.core.pagination import Page, build_page
from quecomemos.features.favorite import service
from quecomemos.features.recipe import service as recipe_service
from quecomemos.features.recipe.schemas import RecipeFilters, RecipeSummary

router = APIRouter(tags=["favorites"])


@router.put("/recipes/{recipe_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def add_favorite(recipe_id: uuid.UUID, current_user: CurrentUser, db: DbSession) -> None:
    await recipe_service.get_visible(db, recipe_id)
    await service.add(db, current_user, recipe_id)


@router.delete("/recipes/{recipe_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(recipe_id: uuid.UUID, current_user: CurrentUser, db: DbSession) -> None:
    await service.remove(db, current_user, recipe_id)


@router.get("/me/favorites", response_model=Page[RecipeSummary])
async def list_favorites(
    current_user: CurrentUser, db: DbSession, filters: Annotated[RecipeFilters, Query()]
) -> Page[RecipeSummary]:
    params = filters.page_params
    rows, total = await service.list_for_user(db, current_user, params, filters)
    return build_page([RecipeSummary.model_validate(row) for row in rows], total, params)
