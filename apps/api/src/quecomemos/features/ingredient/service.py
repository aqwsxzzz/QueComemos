"""Ingredient queries.

Only reads: the taxonomy is seeded and curated by the maintainer, never written
through the API. See docs/ingredients-model.md.
"""

from sqlalchemy import ColumnElement, Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from quecomemos.core.filters import apply_sort
from quecomemos.core.pagination import PageParams, paginate
from quecomemos.core.search import search_clause
from quecomemos.core.text import normalize_for_match
from quecomemos.features.ingredient.models import Ingredient, IngredientAlias
from quecomemos.features.ingredient.schemas import IngredientFilters

SORTABLE = {"name": Ingredient.name, "category": Ingredient.category}
DEFAULT_SORT = "name"
SEARCHABLE = (Ingredient.name,)


def _apply_search(
    statement: Select[tuple[Ingredient]], term: str | None
) -> Select[tuple[Ingredient]]:
    """Matches the display name or any regional alias.

    Someone typing "palta" must find the same ingredient as someone typing
    "aguacate", so the alias table is part of the search, not an afterthought.
    """
    if term is None or not term.strip():
        return statement

    by_alias = select(IngredientAlias.ingredient_id).where(
        IngredientAlias.normalized.startswith(normalize_for_match(term))
    )
    clauses: list[ColumnElement[bool]] = [Ingredient.id.in_(by_alias)]

    by_name = search_clause(SEARCHABLE, term)
    if by_name is not None:
        clauses.append(by_name)

    return statement.where(or_(*clauses))


async def list_ingredients(
    db: AsyncSession, params: PageParams, filters: IngredientFilters
) -> tuple[list[Ingredient], int]:
    statement = select(Ingredient)
    if filters.category is not None:
        statement = statement.where(Ingredient.category == filters.category)

    statement = _apply_search(statement, filters.q)
    return await paginate(db, apply_sort(statement, SORTABLE, filters.sort, DEFAULT_SORT), params)
