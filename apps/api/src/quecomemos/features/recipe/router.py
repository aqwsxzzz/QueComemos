"""Recipe routes. The pool is publicly readable; writing needs an account."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from quecomemos.core.deps import CurrentUser, DbSession
from quecomemos.core.pagination import Page, build_page
from quecomemos.features.recipe import guards, service
from quecomemos.features.recipe.schemas import (
    RecipeCreate,
    RecipeFilters,
    RecipeRead,
    RecipeSummary,
    RecipeUpdate,
)

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("", response_model=Page[RecipeSummary])
async def list_recipes(
    db: DbSession,
    # Query() rather than Depends() so the model's extra="forbid" actually
    # rejects unknown query params instead of silently ignoring them.
    filters: Annotated[RecipeFilters, Query()],
) -> Page[RecipeSummary]:
    """Paginated, searchable and filtered server-side. Anonymous browsing is fine."""
    params = filters.page_params
    rows, total = await service.list_pool(db, params, filters)
    return build_page([RecipeSummary.model_validate(row) for row in rows], total, params)


@router.post("", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    payload: RecipeCreate, current_user: CurrentUser, db: DbSession
) -> RecipeRead:
    recipe = await service.create(db, current_user, payload)
    return RecipeRead.model_validate(recipe)


@router.get("/{recipe_id}", response_model=RecipeRead)
async def read_recipe(recipe_id: uuid.UUID, db: DbSession) -> RecipeRead:
    recipe = await service.get_visible(db, recipe_id)
    return RecipeRead.model_validate(recipe)


@router.patch("/{recipe_id}", response_model=RecipeRead)
async def update_recipe(
    recipe_id: uuid.UUID, payload: RecipeUpdate, current_user: CurrentUser, db: DbSession
) -> RecipeRead:
    recipe = await service.get_for_author(db, recipe_id)
    guards.assert_can_edit(recipe, current_user)
    updated = await service.update(db, recipe, payload)
    return RecipeRead.model_validate(updated)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(recipe_id: uuid.UUID, current_user: CurrentUser, db: DbSession) -> None:
    recipe = await service.get_for_author(db, recipe_id)
    guards.assert_can_edit(recipe, current_user)
    await service.remove(db, recipe)
