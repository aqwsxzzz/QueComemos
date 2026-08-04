"""Matching degrades, never breaks. Real Postgres, seeded taxonomy."""

from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from quecomemos.features.ingredient import matcher
from quecomemos.features.ingredient.models import Ingredient, IngredientReviewQueue
from quecomemos.features.ingredient.seed import seed_ingredients

SEED_DIR = Path(__file__).resolve().parents[1] / "src" / "quecomemos" / "data" / "ingredients"


@pytest.fixture
async def seeded(db: AsyncSession) -> AsyncSession:
    await seed_ingredients(db, SEED_DIR)
    return db


async def _canonical_name(db: AsyncSession, ingredient_id: object) -> str:
    statement = select(Ingredient.name).where(Ingredient.id == ingredient_id)
    return (await db.execute(statement)).scalar_one()


@pytest.mark.parametrize(
    ("typed", "canonical"),
    [
        ("tomate", "tomate"),
        ("tomates", "tomate"),
        ("Tomates", "tomate"),
        ("jitomate", "tomate"),
        ("aguacate", "palta"),
        ("palta", "palta"),
        ("frijoles", "poroto"),
        ("judias", "poroto"),
        ("judías", "poroto"),
        ("elote", "choclo"),
        ("maíz", "choclo"),
        ("fresa", "frutilla"),
        ("frutillas", "frutilla"),
    ],
)
async def test_regional_vocabulary_matches_one_canonical_ingredient(
    seeded: AsyncSession, typed: str, canonical: str
) -> None:
    ingredient_id = await matcher.find_ingredient_id(seeded, typed)

    assert ingredient_id is not None, f"{typed!r} matched nothing"
    assert await _canonical_name(seeded, ingredient_id) == canonical


async def test_an_es_plural_falls_back_to_the_strong_key(seeded: AsyncSession) -> None:
    ingredient_id = await matcher.find_ingredient_id(seeded, "limones")

    assert ingredient_id is not None
    assert await _canonical_name(seeded, ingredient_id) == "limon"


async def test_a_miss_returns_none_and_is_queued_for_review(seeded: AsyncSession) -> None:
    ingredient_id = await matcher.match(seeded, "polvo de estrellas")

    assert ingredient_id is None
    queued = (
        await seeded.execute(
            select(IngredientReviewQueue).where(
                IngredientReviewQueue.normalized == "polvo de estrella"
            )
        )
    ).scalar_one()
    assert queued.hit_count == 1


async def test_repeated_misses_increment_the_same_queue_row(seeded: AsyncSession) -> None:
    await matcher.match(seeded, "polvo de estrellas")
    await matcher.match(seeded, "polvo de estrellas")

    rows = (
        (
            await seeded.execute(
                select(IngredientReviewQueue).where(
                    IngredientReviewQueue.normalized == "polvo de estrella"
                )
            )
        )
        .scalars()
        .all()
    )

    assert len(rows) == 1
    assert rows[0].hit_count == 2


async def test_a_hit_is_not_queued_for_review(seeded: AsyncSession) -> None:
    await matcher.match(seeded, "tomate")

    count = (await seeded.execute(select(IngredientReviewQueue))).scalars().all()

    assert count == []
