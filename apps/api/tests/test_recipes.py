"""Recipe CRUD, the public pool, and the guards around them."""

from typing import Any

import pytest
from httpx import AsyncClient

RECIPE = {
    "title": "Fideos con tuco de los martes",
    "intro": "Lo que sale cuando no hay tiempo.",
    "servings": 4,
    "minutes": 35,
    "ingredients": [
        {"raw_text": "500 g de fideos"},
        {"raw_text": "2 tomates grandes"},
        {"raw_text": "sal a gusto"},
        {"raw_text": "un puñado de amor de la abuela"},
    ],
    "steps": [
        {"text": "Poné a hervir el agua."},
        {"text": "Mientras tanto, hacé el tuco."},
    ],
}


async def _account(client: AsyncClient, prefix: str, email: str) -> dict[str, Any]:
    response = await client.post(
        f"{prefix}/auth/register",
        json={"email": email, "password": "fideos-con-tuco-3", "display_name": email.split("@")[0]},
    )
    body: dict[str, Any] = response.json()
    return body


def _auth(session: dict[str, Any]) -> dict[str, str]:
    return {"Authorization": f"Bearer {session['tokens']['access_token']}"}


async def _create(
    client: AsyncClient, prefix: str, session: dict[str, Any], **overrides: Any
) -> dict[str, Any]:
    response = await client.post(
        f"{prefix}/recipes", json={**RECIPE, **overrides}, headers=_auth(session)
    )
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body


async def test_create_stores_raw_text_exactly_as_typed(
    client: AsyncClient, api_prefix: str
) -> None:
    session = await _account(client, api_prefix, "ana@example.com")

    recipe = await _create(client, api_prefix, session)

    typed = [item["raw_text"] for item in recipe["ingredients"]]
    assert typed == [item["raw_text"] for item in RECIPE["ingredients"]]


async def test_create_extracts_quantity_and_unit_where_it_can(
    client: AsyncClient, api_prefix: str
) -> None:
    session = await _account(client, api_prefix, "ana@example.com")

    recipe = await _create(client, api_prefix, session)
    fideos = recipe["ingredients"][0]

    assert fideos["quantity"] == 500.0
    assert fideos["unit"] == "g"


async def test_an_unmatched_ingredient_still_saves_with_a_null_link(
    client: AsyncClient, api_prefix: str
) -> None:
    session = await _account(client, api_prefix, "ana@example.com")

    recipe = await _create(client, api_prefix, session)
    abuela = recipe["ingredients"][3]

    assert abuela["raw_text"] == "un puñado de amor de la abuela"
    assert abuela["ingredient_id"] is None


async def test_ingredients_and_steps_keep_their_order(
    client: AsyncClient, api_prefix: str
) -> None:
    session = await _account(client, api_prefix, "ana@example.com")

    recipe = await _create(client, api_prefix, session)

    assert [item["position"] for item in recipe["ingredients"]] == [0, 1, 2, 3]
    assert [step["position"] for step in recipe["steps"]] == [0, 1]


async def test_create_requires_authentication(client: AsyncClient, api_prefix: str) -> None:
    response = await client.post(f"{api_prefix}/recipes", json=RECIPE)

    assert response.status_code == 401


@pytest.mark.parametrize(
    "payload",
    [
        {"ingredients": []},
        {"steps": []},
        {"title": "no"},
    ],
)
async def test_create_rejects_incomplete_recipes(
    client: AsyncClient, api_prefix: str, payload: dict[str, Any]
) -> None:
    session = await _account(client, api_prefix, "ana@example.com")

    response = await client.post(
        f"{api_prefix}/recipes", json={**RECIPE, **payload}, headers=_auth(session)
    )

    assert response.status_code == 422


async def test_source_url_must_be_on_the_allowlist(client: AsyncClient, api_prefix: str) -> None:
    session = await _account(client, api_prefix, "ana@example.com")

    blocked = await client.post(
        f"{api_prefix}/recipes",
        json={**RECIPE, "source_url": "https://sitio-cualquiera.example/receta"},
        headers=_auth(session),
    )
    allowed = await client.post(
        f"{api_prefix}/recipes",
        json={**RECIPE, "source_url": "https://www.youtube.com/watch?v=abc"},
        headers=_auth(session),
    )

    assert blocked.status_code == 422
    assert allowed.status_code == 201


async def test_pool_is_readable_without_a_token(client: AsyncClient, api_prefix: str) -> None:
    session = await _account(client, api_prefix, "ana@example.com")
    await _create(client, api_prefix, session)

    response = await client.get(f"{api_prefix}/recipes")

    assert response.status_code == 200
    assert response.json()["meta"]["total"] == 1


async def test_pool_paginates(client: AsyncClient, api_prefix: str) -> None:
    session = await _account(client, api_prefix, "ana@example.com")
    for index in range(3):
        await _create(client, api_prefix, session, title=f"Receta numero {index}")

    response = await client.get(f"{api_prefix}/recipes", params={"page": 1, "page_size": 2})
    body = response.json()

    assert len(body["data"]) == 2
    assert body["meta"] == {"page": 1, "page_size": 2, "total": 3, "has_next": True}


async def test_pool_searches_by_title(client: AsyncClient, api_prefix: str) -> None:
    session = await _account(client, api_prefix, "ana@example.com")
    await _create(client, api_prefix, session, title="Tarta de acelga")
    await _create(client, api_prefix, session, title="Guiso de lentejas")

    response = await client.get(f"{api_prefix}/recipes", params={"q": "acelga"})

    assert response.json()["meta"]["total"] == 1
    assert response.json()["data"][0]["title"] == "Tarta de acelga"


async def test_pool_rejects_a_sort_outside_the_whitelist(
    client: AsyncClient, api_prefix: str
) -> None:
    response = await client.get(f"{api_prefix}/recipes", params={"sort": "password_hash"})

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


async def test_pool_rejects_an_unknown_filter(client: AsyncClient, api_prefix: str) -> None:
    response = await client.get(f"{api_prefix}/recipes", params={"is_maintainer": "true"})

    assert response.status_code == 422


async def test_pool_filters_by_author(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana@example.com")
    beto = await _account(client, api_prefix, "beto@example.com")
    await _create(client, api_prefix, ana, title="Lo de Ana")
    await _create(client, api_prefix, beto, title="Lo de Beto")

    response = await client.get(f"{api_prefix}/recipes", params={"author_id": ana["user"]["id"]})

    assert response.json()["meta"]["total"] == 1
    assert response.json()["data"][0]["title"] == "Lo de Ana"


async def test_pool_summary_does_not_carry_steps(client: AsyncClient, api_prefix: str) -> None:
    session = await _account(client, api_prefix, "ana@example.com")
    await _create(client, api_prefix, session)

    summary = (await client.get(f"{api_prefix}/recipes")).json()["data"][0]

    assert "steps" not in summary
    assert "ingredients" not in summary
    assert summary["author"]["display_name"] == "ana"


async def test_only_the_author_can_edit(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana@example.com")
    beto = await _account(client, api_prefix, "beto@example.com")
    recipe = await _create(client, api_prefix, ana)

    response = await client.patch(
        f"{api_prefix}/recipes/{recipe['id']}", json={"title": "Secuestrada"}, headers=_auth(beto)
    )

    assert response.status_code == 403


async def test_update_replaces_ingredients_and_rematches(
    client: AsyncClient, api_prefix: str
) -> None:
    session = await _account(client, api_prefix, "ana@example.com")
    recipe = await _create(client, api_prefix, session)

    response = await client.patch(
        f"{api_prefix}/recipes/{recipe['id']}",
        json={"ingredients": [{"raw_text": "1 kg de papas"}]},
        headers=_auth(session),
    )

    ingredients = response.json()["ingredients"]
    assert len(ingredients) == 1
    assert ingredients[0]["unit"] == "kg"


async def test_a_removed_recipe_disappears_from_the_pool_and_returns_404(
    client: AsyncClient, api_prefix: str
) -> None:
    session = await _account(client, api_prefix, "ana@example.com")
    recipe = await _create(client, api_prefix, session)

    deleted = await client.delete(f"{api_prefix}/recipes/{recipe['id']}", headers=_auth(session))
    assert deleted.status_code == 204

    assert (await client.get(f"{api_prefix}/recipes")).json()["meta"]["total"] == 0
    assert (await client.get(f"{api_prefix}/recipes/{recipe['id']}")).status_code == 404


async def test_only_the_author_can_delete(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana@example.com")
    beto = await _account(client, api_prefix, "beto@example.com")
    recipe = await _create(client, api_prefix, ana)

    response = await client.delete(f"{api_prefix}/recipes/{recipe['id']}", headers=_auth(beto))

    assert response.status_code == 403
