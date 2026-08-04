"""Comment routes, nested under the recipe they belong to."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from quecomemos.core.deps import CurrentUser, DbSession, MaybeCurrentUser
from quecomemos.core.pagination import Page, build_page
from quecomemos.features.comment import service
from quecomemos.features.comment.schemas import CommentCreate, CommentFilters, CommentRead
from quecomemos.features.recipe import service as recipe_service

router = APIRouter(tags=["comments"])


@router.get("/recipes/{recipe_id}/comments", response_model=Page[CommentRead])
async def list_comments(
    recipe_id: uuid.UUID,
    db: DbSession,
    viewer: MaybeCurrentUser,
    filters: Annotated[CommentFilters, Query()],
) -> Page[CommentRead]:
    """Readable anonymously; a signed-in viewer never sees people they blocked."""
    await recipe_service.get_visible(db, recipe_id)
    params = filters.page_params
    rows, total = await service.list_for_recipe(db, recipe_id, viewer, params, filters)
    return build_page([CommentRead.model_validate(row) for row in rows], total, params)


@router.post(
    "/recipes/{recipe_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    recipe_id: uuid.UUID, payload: CommentCreate, current_user: CurrentUser, db: DbSession
) -> CommentRead:
    recipe = await recipe_service.get_visible(db, recipe_id)
    comment = await service.create(db, current_user, recipe, payload)
    return CommentRead.model_validate(comment)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: uuid.UUID, current_user: CurrentUser, db: DbSession) -> None:
    comment = await service.get(db, comment_id)
    await service.remove(db, comment, current_user)
