"""`uv run python -m quecomemos.scripts.seed` — populate the ingredient taxonomy."""

import asyncio
import logging

from quecomemos.core.db import dispose_engine, get_session_factory
from quecomemos.features.ingredient.seed import seed_ingredients

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    async with get_session_factory()() as session:
        ingredients, aliases = await seed_ingredients(session)
    await dispose_engine()
    logger.info("done: %s ingredients, %s new aliases", ingredients, aliases)


if __name__ == "__main__":
    asyncio.run(main())
