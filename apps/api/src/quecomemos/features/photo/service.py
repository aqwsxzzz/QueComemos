"""Photo business logic: validate, sanitize, store, record."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from quecomemos.core import storage
from quecomemos.core.errors import NotFoundError, ValidationError
from quecomemos.features.photo.images import (
    OUTPUT_CONTENT_TYPE,
    Variant,
    render_variants,
    validate_upload,
)
from quecomemos.features.photo.models import Photo
from quecomemos.features.recipe.models import Recipe, RecipeStep

MAX_PHOTOS_PER_RECIPE = 20


def _keys_for(storage_key: str) -> list[str]:
    return [f"{storage_key}-{variant.value}.webp" for variant in Variant]


async def _assert_step_belongs(db: AsyncSession, recipe_id: uuid.UUID, step_id: uuid.UUID) -> None:
    statement = select(RecipeStep.id).where(
        RecipeStep.id == step_id, RecipeStep.recipe_id == recipe_id
    )
    if (await db.execute(statement)).scalar_one_or_none() is None:
        raise ValidationError("Ese paso no pertenece a esta receta")


async def _next_position(db: AsyncSession, recipe_id: uuid.UUID) -> int:
    statement = select(func.count()).select_from(Photo).where(Photo.recipe_id == recipe_id)
    count = (await db.execute(statement)).scalar_one()
    if count >= MAX_PHOTOS_PER_RECIPE:
        raise ValidationError(f"Una receta puede tener hasta {MAX_PHOTOS_PER_RECIPE} fotos")
    return count


async def add_photo(
    db: AsyncSession,
    recipe: Recipe,
    raw: bytes,
    content_type: str | None,
    step_id: uuid.UUID | None,
    alt_text: str | None,
) -> Photo:
    validate_upload(raw, content_type)
    if step_id is not None:
        await _assert_step_belongs(db, recipe.id, step_id)
    position = await _next_position(db, recipe.id)

    rendered = render_variants(raw)
    storage_key = f"recipes/{recipe.id}/{uuid.uuid4()}"
    for image in rendered:
        await storage.put_object(
            f"{storage_key}-{image.variant.value}.webp", image.data, OUTPUT_CONTENT_TYPE
        )

    full = next(image for image in rendered if image.variant is Variant.FULL)
    photo = Photo(
        recipe_id=recipe.id,
        step_id=step_id,
        storage_key=storage_key,
        width=full.width,
        height=full.height,
        alt_text=alt_text,
        position=position,
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


async def list_for_recipe(db: AsyncSession, recipe_id: uuid.UUID) -> list[Photo]:
    statement = select(Photo).where(Photo.recipe_id == recipe_id).order_by(Photo.position)
    return list((await db.execute(statement)).scalars().all())


async def get(db: AsyncSession, photo_id: uuid.UUID) -> Photo:
    photo = (await db.execute(select(Photo).where(Photo.id == photo_id))).scalar_one_or_none()
    if photo is None:
        raise NotFoundError("Foto no encontrada")
    return photo


async def remove(db: AsyncSession, photo: Photo) -> None:
    """Photos are hard-deleted: the bytes should not outlive the row."""
    keys = _keys_for(photo.storage_key)
    await db.delete(photo)
    await db.commit()
    await storage.delete_objects(keys)


async def purge_for_recipe(db: AsyncSession, recipe_id: uuid.UUID) -> None:
    """Used by moderation when a recipe or an author is taken down."""
    photos = await list_for_recipe(db, recipe_id)
    keys = [key for photo in photos for key in _keys_for(photo.storage_key)]
    for photo in photos:
        await db.delete(photo)
    await db.commit()
    await storage.delete_objects(keys)
