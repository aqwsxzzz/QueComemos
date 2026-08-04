"""Follows, favorites and comments, including the blocked-user filtering."""

from typing import Any

from httpx import AsyncClient

RECIPE = {
    "title": "Guiso de lentejas de domingo",
    "ingredients": [{"raw_text": "300 g de lentejas"}],
    "steps": [{"text": "Remojar la noche anterior."}, {"text": "Cocinar a fuego lento."}],
}


async def _account(client: AsyncClient, prefix: str, name: str) -> dict[str, Any]:
    response = await client.post(
        f"{prefix}/auth/register",
        json={
            "email": f"{name}@example.com",
            "password": "guiso-de-lentejas-6",
            "display_name": name.capitalize(),
        },
    )
    body: dict[str, Any] = response.json()
    return body


def _auth(session: dict[str, Any]) -> dict[str, str]:
    return {"Authorization": f"Bearer {session['tokens']['access_token']}"}


async def _recipe(client: AsyncClient, prefix: str, session: dict[str, Any]) -> dict[str, Any]:
    response = await client.post(f"{prefix}/recipes", json=RECIPE, headers=_auth(session))
    body: dict[str, Any] = response.json()
    return body


# --- follows ------------------------------------------------------------------


async def test_follow_then_unfollow(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")

    followed = await client.put(
        f"{api_prefix}/cooks/{beto['user']['id']}/follow", headers=_auth(ana)
    )
    assert followed.status_code == 204

    status = await client.get(f"{api_prefix}/cooks/{beto['user']['id']}/follow", headers=_auth(ana))
    assert status.json()["is_followed"] is True

    await client.delete(f"{api_prefix}/cooks/{beto['user']['id']}/follow", headers=_auth(ana))
    after = await client.get(f"{api_prefix}/cooks/{beto['user']['id']}/follow", headers=_auth(ana))
    assert after.json()["is_followed"] is False


async def test_following_yourself_is_rejected(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")

    response = await client.put(
        f"{api_prefix}/cooks/{ana['user']['id']}/follow", headers=_auth(ana)
    )

    assert response.status_code == 422


async def test_following_twice_conflicts(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")

    await client.put(f"{api_prefix}/cooks/{beto['user']['id']}/follow", headers=_auth(ana))
    again = await client.put(f"{api_prefix}/cooks/{beto['user']['id']}/follow", headers=_auth(ana))

    assert again.status_code == 409


async def test_unfollowing_someone_you_do_not_follow_is_fine(
    client: AsyncClient, api_prefix: str
) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")

    response = await client.delete(
        f"{api_prefix}/cooks/{beto['user']['id']}/follow", headers=_auth(ana)
    )

    assert response.status_code == 204


async def test_following_list_is_paginated(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    await client.put(f"{api_prefix}/cooks/{beto['user']['id']}/follow", headers=_auth(ana))

    response = await client.get(f"{api_prefix}/me/following", headers=_auth(ana))

    assert response.json()["meta"]["total"] == 1
    assert response.json()["data"][0]["display_name"] == "Beto"
    assert "email" not in response.json()["data"][0]


# --- favorites ----------------------------------------------------------------


async def test_favorite_is_idempotent(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    recipe = await _recipe(client, api_prefix, ana)

    first = await client.put(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(ana))
    second = await client.put(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(ana))

    assert (first.status_code, second.status_code) == (204, 204)
    assert (await client.get(f"{api_prefix}/me/favorites", headers=_auth(ana))).json()["meta"][
        "total"
    ] == 1


async def test_favorites_can_be_removed(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    recipe = await _recipe(client, api_prefix, ana)
    await client.put(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(ana))

    await client.delete(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(ana))

    listing = await client.get(f"{api_prefix}/me/favorites", headers=_auth(ana))
    assert listing.json()["meta"]["total"] == 0


async def test_favoriting_a_missing_recipe_is_404(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")

    response = await client.put(
        f"{api_prefix}/recipes/11111111-1111-1111-1111-111111111111/favorite", headers=_auth(ana)
    )

    assert response.status_code == 404


# --- comments -----------------------------------------------------------------


async def test_comment_appears_on_the_recipe(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)

    created = await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/comments",
        json={"body": "Le puse panceta y quedó bárbaro."},
        headers=_auth(beto),
    )

    assert created.status_code == 201
    assert created.json()["author"]["display_name"] == "Beto"
    listing = await client.get(f"{api_prefix}/recipes/{recipe['id']}/comments")
    assert listing.json()["meta"]["total"] == 1


async def test_a_question_must_name_a_step(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    recipe = await _recipe(client, api_prefix, ana)

    response = await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/comments",
        json={"body": "No entiendo esta parte", "kind": "question"},
        headers=_auth(ana),
    )

    assert response.status_code == 422


async def test_a_question_hangs_off_its_step(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)
    step_id = recipe["steps"][1]["id"]

    created = await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/comments",
        json={"body": "¿Cuánto es fuego lento?", "kind": "question", "step_id": step_id},
        headers=_auth(beto),
    )

    assert created.status_code == 201
    assert created.json()["step_id"] == step_id

    filtered = await client.get(
        f"{api_prefix}/recipes/{recipe['id']}/comments", params={"kind": "question"}
    )
    assert filtered.json()["meta"]["total"] == 1


async def test_a_step_from_another_recipe_is_rejected(
    client: AsyncClient, api_prefix: str
) -> None:
    ana = await _account(client, api_prefix, "ana")
    mine = await _recipe(client, api_prefix, ana)
    other = await _recipe(client, api_prefix, ana)

    response = await client.post(
        f"{api_prefix}/recipes/{mine['id']}/comments",
        json={"body": "¿Y acá?", "kind": "question", "step_id": other["steps"][0]["id"]},
        headers=_auth(ana),
    )

    assert response.status_code == 422


async def test_commenting_requires_authentication(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    recipe = await _recipe(client, api_prefix, ana)

    response = await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/comments", json={"body": "Hola"}
    )

    assert response.status_code == 401


async def test_the_recipe_owner_can_remove_a_comment(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)
    comment = await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/comments",
        json={"body": "spam spam spam"},
        headers=_auth(beto),
    )

    removed = await client.delete(
        f"{api_prefix}/comments/{comment.json()['id']}", headers=_auth(ana)
    )

    assert removed.status_code == 204
    listing = await client.get(f"{api_prefix}/recipes/{recipe['id']}/comments")
    assert listing.json()["meta"]["total"] == 0


async def test_a_stranger_cannot_remove_a_comment(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    caro = await _account(client, api_prefix, "caro")
    recipe = await _recipe(client, api_prefix, ana)
    comment = await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/comments",
        json={"body": "Buenísima"},
        headers=_auth(beto),
    )

    response = await client.delete(
        f"{api_prefix}/comments/{comment.json()['id']}", headers=_auth(caro)
    )

    assert response.status_code == 403


async def test_commenting_on_a_removed_recipe_is_404(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    recipe = await _recipe(client, api_prefix, ana)
    await client.delete(f"{api_prefix}/recipes/{recipe['id']}", headers=_auth(ana))

    response = await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/comments",
        json={"body": "Hola"},
        headers=_auth(ana),
    )

    assert response.status_code == 404
