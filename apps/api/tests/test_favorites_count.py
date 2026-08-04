"""The denormalized `favorites_count` on a recipe.

A counter that drifts is worse than no counter, so the cases that matter are
the repeated ones: saving twice, unsaving twice, and unsaving what was never
saved.
"""

from typing import Any

from httpx import AsyncClient

RECIPE = {
    "title": "Tortilla de papas de las apuradas",
    "ingredients": [{"raw_text": "4 papas"}, {"raw_text": "3 huevos"}],
    "steps": [{"text": "Freír las papas."}, {"text": "Mezclar con el huevo."}],
}


async def _account(client: AsyncClient, prefix: str, name: str) -> dict[str, Any]:
    response = await client.post(
        f"{prefix}/auth/register",
        json={
            "email": f"{name}@example.com",
            "password": "tortilla-de-papas-7",
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


async def _count(client: AsyncClient, prefix: str, recipe_id: str) -> int:
    response = await client.get(f"{prefix}/recipes/{recipe_id}")
    count: int = response.json()["favorites_count"]
    return count


async def test_a_new_recipe_starts_with_no_favorites(
    client: AsyncClient, api_prefix: str
) -> None:
    ana = await _account(client, api_prefix, "ana")
    recipe = await _recipe(client, api_prefix, ana)

    assert recipe["favorites_count"] == 0


async def test_favoriting_a_recipe_increments_its_favorites_count(
    client: AsyncClient, api_prefix: str
) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)

    await client.put(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(beto))

    assert await _count(client, api_prefix, recipe["id"]) == 1


async def test_two_cooks_favoriting_the_same_recipe_counts_both(
    client: AsyncClient, api_prefix: str
) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    caro = await _account(client, api_prefix, "caro")
    recipe = await _recipe(client, api_prefix, ana)

    await client.put(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(beto))
    await client.put(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(caro))

    assert await _count(client, api_prefix, recipe["id"]) == 2


async def test_favoriting_twice_counts_once(client: AsyncClient, api_prefix: str) -> None:
    """Saving is idempotent, so the second PUT must not bump the counter."""
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)

    await client.put(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(beto))
    await client.put(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(beto))

    assert await _count(client, api_prefix, recipe["id"]) == 1


async def test_unfavoriting_a_recipe_decrements_its_favorites_count(
    client: AsyncClient, api_prefix: str
) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)
    await client.put(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(beto))

    await client.delete(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(beto))

    assert await _count(client, api_prefix, recipe["id"]) == 0


async def test_unfavoriting_twice_does_not_drive_the_count_negative(
    client: AsyncClient, api_prefix: str
) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)
    await client.put(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(beto))

    await client.delete(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(beto))
    await client.delete(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(beto))

    assert await _count(client, api_prefix, recipe["id"]) == 0


async def test_unfavoriting_something_never_saved_leaves_the_count_alone(
    client: AsyncClient, api_prefix: str
) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)

    await client.delete(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(beto))

    assert await _count(client, api_prefix, recipe["id"]) == 0


async def test_the_pool_listing_carries_the_favorites_count(
    client: AsyncClient, api_prefix: str
) -> None:
    """The card renders it, so it has to survive the summary schema too."""
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)
    await client.put(f"{api_prefix}/recipes/{recipe['id']}/favorite", headers=_auth(beto))

    response = await client.get(f"{api_prefix}/recipes")

    assert response.json()["data"][0]["favorites_count"] == 1
