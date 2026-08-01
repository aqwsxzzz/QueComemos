"""Account routes and the current-user dependency."""

import uuid
from datetime import UTC, datetime
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from quecomemos.core.security import create_token
from quecomemos.features.user import service as user_service
from quecomemos.features.user.schemas import UserCreate

REGISTRATION = {
    "email": "beto@example.com",
    "password": "milanesa-napolitana-1",
    "display_name": "Beto",
}


async def _register(client: AsyncClient, prefix: str) -> dict[str, Any]:
    response = await client.post(f"{prefix}/auth/register", json=REGISTRATION)
    body: dict[str, Any] = response.json()
    return body


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_me_returns_the_authenticated_account(client: AsyncClient, api_prefix: str) -> None:
    session = await _register(client, api_prefix)

    response = await client.get(
        f"{api_prefix}/users/me", headers=_auth(session["tokens"]["access_token"])
    )

    assert response.status_code == 200
    assert response.json()["email"] == "beto@example.com"


async def test_me_requires_a_token(client: AsyncClient, api_prefix: str) -> None:
    response = await client.get(f"{api_prefix}/users/me")

    assert response.status_code == 401
    assert response.json()["code"] == "unauthenticated"


async def test_me_rejects_a_refresh_token(client: AsyncClient, api_prefix: str) -> None:
    session = await _register(client, api_prefix)

    response = await client.get(
        f"{api_prefix}/users/me", headers=_auth(session["tokens"]["refresh_token"])
    )

    assert response.status_code == 401


async def test_me_rejects_a_token_for_a_deleted_account(
    client: AsyncClient, api_prefix: str
) -> None:
    orphan_token, _ = create_token(uuid.uuid4(), "access")

    response = await client.get(f"{api_prefix}/users/me", headers=_auth(orphan_token))

    assert response.status_code == 401


async def test_update_me_changes_the_profile(client: AsyncClient, api_prefix: str) -> None:
    session = await _register(client, api_prefix)
    headers = _auth(session["tokens"]["access_token"])

    response = await client.patch(
        f"{api_prefix}/users/me", json={"bio": "Cocino los domingos"}, headers=headers
    )

    assert response.status_code == 200
    assert response.json()["bio"] == "Cocino los domingos"
    assert response.json()["display_name"] == "Beto"


async def test_update_me_rejects_unknown_fields(client: AsyncClient, api_prefix: str) -> None:
    session = await _register(client, api_prefix)

    response = await client.patch(
        f"{api_prefix}/users/me",
        json={"is_maintainer": True},
        headers=_auth(session["tokens"]["access_token"]),
    )

    assert response.status_code == 422


async def test_public_profile_hides_the_email(client: AsyncClient, api_prefix: str) -> None:
    session = await _register(client, api_prefix)

    response = await client.get(f"{api_prefix}/users/{session['user']['id']}")

    assert response.status_code == 200
    assert "email" not in response.json()
    assert response.json()["display_name"] == "Beto"


@pytest.mark.parametrize("field", ["removed_at", "is_active"])
async def test_removed_or_deactivated_accounts_cannot_authenticate(
    client: AsyncClient, api_prefix: str, db: AsyncSession, field: str
) -> None:
    session = await _register(client, api_prefix)
    user = await user_service.get_by_email(db, REGISTRATION["email"])
    assert user is not None

    setattr(user, field, datetime.now(UTC) if field == "removed_at" else False)
    await db.commit()

    response = await client.get(
        f"{api_prefix}/users/me", headers=_auth(session["tokens"]["access_token"])
    )

    assert response.status_code == 401


async def test_service_create_hashes_the_password(db: AsyncSession) -> None:
    user = await user_service.create(
        db,
        UserCreate(email="caro@example.com", password="tarta-de-acelga-7", display_name="Caro"),
    )

    assert user.password_hash != "tarta-de-acelga-7"
    assert user.password_hash.startswith("$2b$")
