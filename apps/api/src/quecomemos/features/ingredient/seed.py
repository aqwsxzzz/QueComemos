"""Load the curated ingredient files and upsert them.

Idempotent: re-running adds new entries and new aliases without duplicating or
destroying anything already matched by existing recipes.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from quecomemos.core.text import normalize_for_match
from quecomemos.features.ingredient.models import Ingredient, IngredientAlias

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "ingredients"


@dataclass(frozen=True, slots=True)
class SeedIngredient:
    name: str
    category: str
    aliases: tuple[str, ...]

    @property
    def slug(self) -> str:
        return normalize_for_match(self.name)


def _parse_file(path: Path) -> list[SeedIngredient]:
    document: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    category = str(document["category"])
    return [
        SeedIngredient(
            name=str(item["name"]),
            category=category,
            aliases=tuple(str(alias) for alias in item.get("aliases") or ()),
        )
        for item in document["items"]
    ]


def load_seed_ingredients(data_dir: Path = DATA_DIR) -> list[SeedIngredient]:
    seeds: list[SeedIngredient] = []
    for path in sorted(data_dir.glob("*.yaml")):
        seeds.extend(_parse_file(path))
    return seeds


async def _upsert_ingredient(db: AsyncSession, seed: SeedIngredient) -> Ingredient:
    existing = (
        await db.execute(select(Ingredient).where(Ingredient.slug == seed.slug))
    ).scalar_one_or_none()
    if existing is not None:
        existing.category = seed.category
        return existing

    ingredient = Ingredient(name=seed.name, slug=seed.slug, category=seed.category)
    db.add(ingredient)
    await db.flush()
    return ingredient


async def _upsert_aliases(db: AsyncSession, ingredient: Ingredient, seed: SeedIngredient) -> int:
    # The canonical name is itself a matchable alias.
    forms = {normalize_for_match(form) for form in (seed.name, *seed.aliases)}
    known = set(
        (
            await db.execute(
                select(IngredientAlias.normalized).where(IngredientAlias.normalized.in_(forms))
            )
        )
        .scalars()
        .all()
    )
    new_forms = forms - known
    db.add_all(
        IngredientAlias(ingredient_id=ingredient.id, normalized=form) for form in sorted(new_forms)
    )
    return len(new_forms)


async def seed_ingredients(db: AsyncSession, data_dir: Path = DATA_DIR) -> tuple[int, int]:
    """Returns (ingredients seen, aliases created)."""
    seeds = load_seed_ingredients(data_dir)
    aliases_created = 0
    for seed in seeds:
        ingredient = await _upsert_ingredient(db, seed)
        aliases_created += await _upsert_aliases(db, ingredient, seed)
    await db.commit()
    logger.info("seeded %s ingredients, %s new aliases", len(seeds), aliases_created)
    return len(seeds), aliases_created
