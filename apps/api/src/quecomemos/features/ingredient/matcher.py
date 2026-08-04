"""Resolve a free-text ingredient line to a canonical ingredient.

The load-bearing rule from docs/ingredients-model.md: a miss is never an error.
`raw_text` is already stored; failing to match simply leaves `ingredient_id`
NULL and records the normalized form for the maintainer to review later.
"""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from quecomemos.core.text import match_candidates
from quecomemos.features.ingredient.models import IngredientAlias, IngredientReviewQueue

logger = logging.getLogger(__name__)


async def find_ingredient_id(db: AsyncSession, text: str) -> uuid.UUID | None:
    """Tries the conservative matching key first, then the stronger fallback."""
    candidates = match_candidates(text)
    if not candidates:
        return None

    statement = select(IngredientAlias.normalized, IngredientAlias.ingredient_id).where(
        IngredientAlias.normalized.in_(candidates)
    )
    hits: dict[str, uuid.UUID] = {
        normalized: ingredient_id for normalized, ingredient_id in await db.execute(statement)
    }

    for candidate in candidates:
        if candidate in hits:
            return hits[candidate]
    return None


async def record_unmatched(db: AsyncSession, text: str) -> None:
    """Upsert into the review queue, counting how often the form shows up."""
    candidates = match_candidates(text)
    if not candidates:
        return

    statement = (
        pg_insert(IngredientReviewQueue)
        .values(normalized=candidates[0], sample_raw_text=text[:255], hit_count=1)
        .on_conflict_do_update(
            index_elements=[IngredientReviewQueue.normalized],
            set_={"hit_count": IngredientReviewQueue.hit_count + 1},
        )
    )
    await db.execute(statement)


async def match(db: AsyncSession, raw_text: str) -> uuid.UUID | None:
    """The one call sites use. Never raises on a miss, never mutates raw_text."""
    ingredient_id = await find_ingredient_id(db, raw_text)
    if ingredient_id is None:
        await record_unmatched(db, raw_text)
        logger.debug("ingredient unmatched, queued for review: %r", raw_text)
    return ingredient_id
