"""Photo routes, nested under the recipe they belong to."""

import uuid
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile, status

from quecomemos.core.deps import CurrentUser, DbSession
from quecomemos.features.photo import service
from quecomemos.features.photo.schemas import PhotoRead
from quecomemos.features.recipe import guards
from quecomemos.features.recipe import service as recipe_service

router = APIRouter(tags=["photos"])


@router.get("/recipes/{recipe_id}/photos", response_model=list[PhotoRead])
async def list_photos(recipe_id: uuid.UUID, db: DbSession) -> list[PhotoRead]:
    await recipe_service.get_visible(db, recipe_id)
    photos = await service.list_for_recipe(db, recipe_id)
    return [PhotoRead.from_model(photo) for photo in photos]


@router.post(
    "/recipes/{recipe_id}/photos",
    response_model=PhotoRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_photo(
    recipe_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
    file: Annotated[UploadFile, File()],
    step_id: Annotated[uuid.UUID | None, Form()] = None,
    alt_text: Annotated[str | None, Form(max_length=200)] = None,
) -> PhotoRead:
    """Photos of the process are the point, so a photo can name its step."""
    recipe = await recipe_service.get_for_author(db, recipe_id)
    guards.assert_can_edit(recipe, current_user)

    photo = await service.add_photo(
        db, recipe, await file.read(), file.content_type, step_id, alt_text
    )
    return PhotoRead.from_model(photo)


@router.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(photo_id: uuid.UUID, current_user: CurrentUser, db: DbSession) -> None:
    photo = await service.get(db, photo_id)
    recipe = await recipe_service.get_for_author(db, photo.recipe_id)
    guards.assert_can_edit(recipe, current_user)
    await service.remove(db, photo)
