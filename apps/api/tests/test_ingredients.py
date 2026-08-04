"""The public ingredient lookup that backs the pool's ingredient filter."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from quecomemos.features.ingredient.models import Ingredient, IngredientAlias


async def _ingredient(
    db: AsyncSession, name: str, slug: str, aliases: list[str], category: str | None = None
) -> Ingredient:
    row = Ingredient(name=name, slug=slug, category=category)
    row.aliases = [IngredientAlias(normalized=alias) for alias in aliases]
    db.add(row)
    await db.commit()
    return row


async def test_list_ingredients_without_a_search_returns_the_taxonomy(
    client: AsyncClient, api_prefix: str, db: AsyncSession
) -> None:
    await _ingredient(db, "Pollo", "pollo", ["pollo"], category="carne")

    response = await client.get(f"{api_prefix}/ingredients")

    assert response.status_code == 200
    assert [row["name"] for row in response.json()["data"]] == ["Pollo"]


async def test_list_ingredients_matching_a_regional_alias_returns_the_canonical_one(
    client: AsyncClient, api_prefix: str, db: AsyncSession
) -> None:
    """Someone typing "palta" must land on the same row as someone typing
    "aguacate" — that is the whole point of the alias table."""
    await _ingredient(db, "Palta", "palta", ["palta", "aguacate"])

    response = await client.get(f"{api_prefix}/ingredients", params={"q": "aguacate"})

    assert [row["name"] for row in response.json()["data"]] == ["Palta"]


async def test_list_ingredients_matching_the_display_name_returns_it(
    client: AsyncClient, api_prefix: str, db: AsyncSession
) -> None:
    await _ingredient(db, "Zanahoria", "zanahoria", ["zanahoria"])

    response = await client.get(f"{api_prefix}/ingredients", params={"q": "zanah"})

    assert [row["name"] for row in response.json()["data"]] == ["Zanahoria"]


async def test_list_ingredients_with_a_non_matching_search_returns_nothing(
    client: AsyncClient, api_prefix: str, db: AsyncSession
) -> None:
    await _ingredient(db, "Pollo", "pollo", ["pollo"])

    response = await client.get(f"{api_prefix}/ingredients", params={"q": "berenjena"})

    assert response.json()["data"] == []
    assert response.json()["meta"]["total"] == 0


async def test_list_ingredients_filtered_by_category_excludes_other_categories(
    client: AsyncClient, api_prefix: str, db: AsyncSession
) -> None:
    await _ingredient(db, "Pollo", "pollo", ["pollo"], category="carne")
    await _ingredient(db, "Zanahoria", "zanahoria", ["zanahoria"], category="verdura")

    response = await client.get(f"{api_prefix}/ingredients", params={"category": "verdura"})

    assert [row["name"] for row in response.json()["data"]] == ["Zanahoria"]


async def test_list_ingredients_never_exposes_the_matching_slug(
    client: AsyncClient, api_prefix: str, db: AsyncSession
) -> None:
    """`slug` is a matching key, not something a client should render."""
    await _ingredient(db, "Pollo", "pollo", ["pollo"])

    response = await client.get(f"{api_prefix}/ingredients")

    assert "slug" not in response.json()["data"][0]


async def test_list_ingredients_with_an_unknown_sort_is_rejected(
    client: AsyncClient, api_prefix: str
) -> None:
    """Sorting is a whitelist — an arbitrary column name must not reach SQL."""
    response = await client.get(f"{api_prefix}/ingredients", params={"sort": "password"})

    assert response.status_code == 422


async def test_list_ingredients_with_an_unknown_query_param_is_rejected(
    client: AsyncClient, api_prefix: str
) -> None:
    response = await client.get(f"{api_prefix}/ingredients", params={"nope": "1"})

    assert response.status_code == 422
