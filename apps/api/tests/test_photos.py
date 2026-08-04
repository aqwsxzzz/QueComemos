"""Photo uploads. Storage is real MinIO from docker-compose, not a mock."""

import io
from typing import Any

import piexif
import pytest
from httpx import AsyncClient
from PIL import Image

from quecomemos.core.errors import ValidationError
from quecomemos.features.photo.images import Variant, render_variants, validate_upload

RECIPE = {
    "title": "Tortilla de papas de la abuela",
    "ingredients": [{"raw_text": "4 huevos"}],
    "steps": [{"text": "Cortar las papas finitas."}, {"text": "Cocinar a fuego bajo."}],
}


def _image_bytes(width: int = 2400, height: int = 1600, fmt: str = "JPEG") -> bytes:
    image = Image.new("RGB", (width, height), (200, 90, 40))
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def _image_with_gps() -> bytes:
    """A photo carrying the coordinates of somebody's kitchen."""
    exif = {
        "0th": {piexif.ImageIFD.Make: b"TestPhone"},
        "Exif": {},
        "GPS": {
            piexif.GPSIFD.GPSLatitudeRef: b"S",
            piexif.GPSIFD.GPSLatitude: ((34, 1), (36, 1), (0, 1)),
            piexif.GPSIFD.GPSLongitudeRef: b"W",
            piexif.GPSIFD.GPSLongitude: ((58, 1), (22, 1), (0, 1)),
        },
        "1st": {},
        "thumbnail": None,
    }
    buffer = io.BytesIO()
    Image.new("RGB", (1200, 800), (10, 120, 90)).save(buffer, format="JPEG", exif=piexif.dump(exif))
    return buffer.getvalue()


async def _account(
    client: AsyncClient, prefix: str, email: str = "ana@example.com"
) -> dict[str, Any]:
    response = await client.post(
        f"{prefix}/auth/register",
        json={"email": email, "password": "tortilla-de-papas-4", "display_name": "Ana"},
    )
    body: dict[str, Any] = response.json()
    return body


def _auth(session: dict[str, Any]) -> dict[str, str]:
    return {"Authorization": f"Bearer {session['tokens']['access_token']}"}


async def _recipe(client: AsyncClient, prefix: str, session: dict[str, Any]) -> dict[str, Any]:
    response = await client.post(f"{prefix}/recipes", json=RECIPE, headers=_auth(session))
    body: dict[str, Any] = response.json()
    return body


# --- pure image pipeline ------------------------------------------------------


def test_exif_gps_never_survives_processing() -> None:
    original = _image_with_gps()
    assert piexif.load(original)["GPS"], "fixture should start with GPS data"

    for rendered in render_variants(original):
        reopened = Image.open(io.BytesIO(rendered.data))
        assert not reopened.getexif(), f"{rendered.variant} kept EXIF"


def test_variants_are_capped_and_keep_aspect_ratio() -> None:
    rendered = {image.variant: image for image in render_variants(_image_bytes(2400, 1200))}

    assert rendered[Variant.THUMB].width == 320
    assert rendered[Variant.CARD].width == 800
    assert rendered[Variant.FULL].width == 1600
    assert rendered[Variant.FULL].height == 800


def test_a_small_image_is_not_upscaled() -> None:
    rendered = {image.variant: image for image in render_variants(_image_bytes(200, 100))}

    assert rendered[Variant.FULL].width == 200


@pytest.mark.parametrize("content_type", ["application/pdf", "text/html", None])
def test_non_images_are_rejected(content_type: str | None) -> None:
    with pytest.raises(ValidationError):
        validate_upload(b"whatever", content_type)


def test_oversize_uploads_are_rejected() -> None:
    with pytest.raises(ValidationError):
        validate_upload(b"x" * (8 * 1024 * 1024 + 1), "image/jpeg")


def test_corrupt_image_data_is_rejected() -> None:
    with pytest.raises(ValidationError):
        render_variants(b"not really a jpeg")


# --- endpoint -----------------------------------------------------------------


async def test_upload_returns_urls_for_every_variant(client: AsyncClient, api_prefix: str) -> None:
    session = await _account(client, api_prefix)
    recipe = await _recipe(client, api_prefix, session)

    response = await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/photos",
        files={"file": ("plato.jpg", _image_bytes(), "image/jpeg")},
        headers=_auth(session),
    )

    assert response.status_code == 201, response.text
    urls = response.json()["urls"]
    assert set(urls) == {"thumb", "card", "full"}
    assert all(url.endswith(".webp") for url in urls.values())


async def test_a_photo_can_belong_to_a_step(client: AsyncClient, api_prefix: str) -> None:
    session = await _account(client, api_prefix)
    recipe = await _recipe(client, api_prefix, session)
    step_id = recipe["steps"][1]["id"]

    response = await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/photos",
        files={"file": ("paso.jpg", _image_bytes(), "image/jpeg")},
        data={"step_id": step_id, "alt_text": "La papa dorándose"},
        headers=_auth(session),
    )

    assert response.status_code == 201
    assert response.json()["step_id"] == step_id
    assert response.json()["alt_text"] == "La papa dorándose"


async def test_a_step_from_another_recipe_is_rejected(client: AsyncClient, api_prefix: str) -> None:
    session = await _account(client, api_prefix)
    mine = await _recipe(client, api_prefix, session)
    other = await _recipe(client, api_prefix, session)

    response = await client.post(
        f"{api_prefix}/recipes/{mine['id']}/photos",
        files={"file": ("paso.jpg", _image_bytes(), "image/jpeg")},
        data={"step_id": other["steps"][0]["id"]},
        headers=_auth(session),
    )

    assert response.status_code == 422


async def test_only_the_author_can_upload(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana@example.com")
    beto = await _account(client, api_prefix, "beto@example.com")
    recipe = await _recipe(client, api_prefix, ana)

    response = await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/photos",
        files={"file": ("plato.jpg", _image_bytes(), "image/jpeg")},
        headers=_auth(beto),
    )

    assert response.status_code == 403


async def test_upload_requires_authentication(client: AsyncClient, api_prefix: str) -> None:
    session = await _account(client, api_prefix)
    recipe = await _recipe(client, api_prefix, session)

    response = await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/photos",
        files={"file": ("plato.jpg", _image_bytes(), "image/jpeg")},
    )

    assert response.status_code == 401


async def test_photos_are_listed_in_order(client: AsyncClient, api_prefix: str) -> None:
    session = await _account(client, api_prefix)
    recipe = await _recipe(client, api_prefix, session)
    for _ in range(3):
        await client.post(
            f"{api_prefix}/recipes/{recipe['id']}/photos",
            files={"file": ("p.jpg", _image_bytes(600, 400), "image/jpeg")},
            headers=_auth(session),
        )

    response = await client.get(f"{api_prefix}/recipes/{recipe['id']}/photos")

    assert [photo["position"] for photo in response.json()] == [0, 1, 2]


async def test_delete_removes_the_photo(client: AsyncClient, api_prefix: str) -> None:
    session = await _account(client, api_prefix)
    recipe = await _recipe(client, api_prefix, session)
    uploaded = await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/photos",
        files={"file": ("plato.jpg", _image_bytes(600, 400), "image/jpeg")},
        headers=_auth(session),
    )

    deleted = await client.delete(
        f"{api_prefix}/photos/{uploaded.json()['id']}", headers=_auth(session)
    )

    assert deleted.status_code == 204
    assert (await client.get(f"{api_prefix}/recipes/{recipe['id']}/photos")).json() == []
