"""Image processing. Pure functions over bytes — no storage, no database.

EXIF is stripped on every upload. Phone photos carry GPS coordinates of the
kitchen they were taken in, and this is a public pool.
"""

import io
from dataclasses import dataclass
from enum import StrEnum

from PIL import Image, ImageOps, UnidentifiedImageError

from quecomemos.core.errors import ValidationError

MAX_UPLOAD_BYTES = 8 * 1024 * 1024
ACCEPTED_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
OUTPUT_CONTENT_TYPE = "image/webp"


class Variant(StrEnum):
    THUMB = "thumb"
    CARD = "card"
    FULL = "full"


VARIANT_WIDTHS: dict[Variant, int] = {
    Variant.THUMB: 320,
    Variant.CARD: 800,
    Variant.FULL: 1600,
}


@dataclass(frozen=True, slots=True)
class RenderedImage:
    variant: Variant
    data: bytes
    width: int
    height: int


def _open_sanitized(raw: bytes) -> Image.Image:
    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError("No pudimos leer esa imagen") from exc

    # Apply the EXIF orientation first, then drop metadata entirely: rotating
    # afterwards would be impossible once the tag is gone.
    rotated = ImageOps.exif_transpose(image) or image
    return rotated.convert("RGB")


def _resize(image: Image.Image, width: int) -> Image.Image:
    if image.width <= width:
        return image.copy()
    height = round(image.height * width / image.width)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def _encode(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    # No exif= argument, so nothing from the original survives.
    image.save(buffer, format="WEBP", quality=82, method=4)
    return buffer.getvalue()


def validate_upload(raw: bytes, content_type: str | None) -> None:
    if content_type not in ACCEPTED_CONTENT_TYPES:
        raise ValidationError("Solo aceptamos imágenes JPG, PNG o WebP")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValidationError("La imagen no puede pesar más de 8 MB")
    if not raw:
        raise ValidationError("El archivo está vacío")


def render_variants(raw: bytes) -> list[RenderedImage]:
    """Returns every variant, EXIF-free, encoded as WebP."""
    source = _open_sanitized(raw)
    rendered: list[RenderedImage] = []
    for variant, width in VARIANT_WIDTHS.items():
        resized = _resize(source, width)
        rendered.append(
            RenderedImage(
                variant=variant,
                data=_encode(resized),
                width=resized.width,
                height=resized.height,
            )
        )
    return rendered
