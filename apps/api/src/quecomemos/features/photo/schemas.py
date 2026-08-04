"""Photo response shapes. Clients get URLs, never storage keys."""

import uuid

from pydantic import BaseModel, ConfigDict, Field

from quecomemos.core.storage import public_url
from quecomemos.features.photo.images import Variant
from quecomemos.features.photo.models import Photo


class PhotoRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    step_id: uuid.UUID | None
    alt_text: str | None
    width: int
    height: int
    position: int
    urls: dict[str, str]

    @classmethod
    def from_model(cls, photo: Photo) -> PhotoRead:
        return cls(
            id=photo.id,
            step_id=photo.step_id,
            alt_text=photo.alt_text,
            width=photo.width,
            height=photo.height,
            position=photo.position,
            urls={
                variant.value: public_url(f"{photo.storage_key}-{variant.value}.webp")
                for variant in Variant
            },
        )


class PhotoUpload(BaseModel):
    """Multipart form fields that travel alongside the file."""

    model_config = ConfigDict(extra="forbid")

    step_id: uuid.UUID | None = None
    alt_text: str | None = Field(default=None, max_length=200)
