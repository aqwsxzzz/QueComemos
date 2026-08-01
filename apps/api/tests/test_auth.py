"""Auth flows against real Postgres."""

from typing import Any

from httpx import AsyncClient

REGISTRATION = {
    "email": "Ana@Example.com",
    "password": "arroz-con-pollo-9",
    "display_name": "Ana",
}


async def _register(client: AsyncClient, prefix: str, **overrides: Any) -> dict[str, Any]:
    response = await client.post(f"{prefix}/auth/register", json={**REGISTRATION, **overrides})
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body


async def test_register_returns_session_and_normalizes_email(
    client: AsyncClient, api_prefix: str
) -> None:
    body = await _register(client, api_prefix)

    assert body["user"]["email"] == "ana@example.com"
    assert body["user"]["display_name"] == "Ana"
    assert body["tokens"]["access_token"]
    assert body["tokens"]["refresh_token"]


async def test_register_never_returns_the_password_hash(
    client: AsyncClient, api_prefix: str
) -> None:
    body = await _register(client, api_prefix)

    assert "password_hash" not in body["user"]
    assert "password" not in body["user"]


async def test_register_rejects_a_duplicate_email(client: AsyncClient, api_prefix: str) -> None:
    await _register(client, api_prefix)

    response = await client.post(f"{api_prefix}/auth/register", json=REGISTRATION)

    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


async def test_register_rejects_a_short_password(client: AsyncClient, api_prefix: str) -> None:
    response = await client.post(
        f"{api_prefix}/auth/register", json={**REGISTRATION, "password": "corto"}
    )

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


async def test_login_succeeds_with_a_differently_cased_email(
    client: AsyncClient, api_prefix: str
) -> None:
    await _register(client, api_prefix)

    response = await client.post(
        f"{api_prefix}/auth/login",
        json={"email": "ANA@example.com", "password": REGISTRATION["password"]},
    )

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "ana@example.com"


async def test_login_rejects_a_wrong_password(client: AsyncClient, api_prefix: str) -> None:
    await _register(client, api_prefix)

    response = await client.post(
        f"{api_prefix}/auth/login",
        json={"email": REGISTRATION["email"], "password": "no-es-la-clave"},
    )

    assert response.status_code == 401


async def test_login_does_not_reveal_whether_the_account_exists(
    client: AsyncClient, api_prefix: str
) -> None:
    await _register(client, api_prefix)

    wrong_password = await client.post(
        f"{api_prefix}/auth/login",
        json={"email": REGISTRATION["email"], "password": "no-es-la-clave"},
    )
    unknown_account = await client.post(
        f"{api_prefix}/auth/login",
        json={"email": "nadie@example.com", "password": "no-es-la-clave"},
    )

    assert wrong_password.json() == unknown_account.json()


async def test_refresh_rotates_and_revokes_the_old_token(
    client: AsyncClient, api_prefix: str
) -> None:
    session = await _register(client, api_prefix)
    original = session["tokens"]["refresh_token"]

    first = await client.post(f"{api_prefix}/auth/refresh", json={"refresh_token": original})
    assert first.status_code == 200
    assert first.json()["refresh_token"] != original

    reused = await client.post(f"{api_prefix}/auth/refresh", json={"refresh_token": original})
    assert reused.status_code == 401


async def test_refresh_rejects_an_access_token(client: AsyncClient, api_prefix: str) -> None:
    session = await _register(client, api_prefix)

    response = await client.post(
        f"{api_prefix}/auth/refresh",
        json={"refresh_token": session["tokens"]["access_token"]},
    )

    assert response.status_code == 401


async def test_logout_revokes_the_refresh_token(client: AsyncClient, api_prefix: str) -> None:
    session = await _register(client, api_prefix)
    token = session["tokens"]["refresh_token"]

    logout = await client.post(f"{api_prefix}/auth/logout", json={"refresh_token": token})
    assert logout.status_code == 204

    reused = await client.post(f"{api_prefix}/auth/refresh", json={"refresh_token": token})
    assert reused.status_code == 401


async def test_logout_is_idempotent(client: AsyncClient, api_prefix: str) -> None:
    session = await _register(client, api_prefix)
    token = session["tokens"]["refresh_token"]

    await client.post(f"{api_prefix}/auth/logout", json={"refresh_token": token})
    again = await client.post(f"{api_prefix}/auth/logout", json={"refresh_token": token})

    assert again.status_code == 204
