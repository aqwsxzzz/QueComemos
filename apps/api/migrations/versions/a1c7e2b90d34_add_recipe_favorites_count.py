"""add recipe favorites_count

Denormalized counter for how many cooks saved a recipe. The pool shows it, and
a later release will sort by it — counting `favorite` rows per recipe at read
time would fan out against the ingredient-filter subquery.

The default is a constant, so on PG 11+ ADD COLUMN is instant (no table
rewrite). Existing rows still need their real count, hence the backfill.

Revision ID: a1c7e2b90d34
Revises: f5040caf1822
Create Date: 2026-08-04 17:02:10.884511
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1c7e2b90d34"
down_revision: str | None = "f5040caf1822"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "recipe",
        sa.Column(
            "favorites_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    # One statement is right at this size. If `favorite` ever grows past a few
    # hundred thousand rows, batch this by recipe id range instead.
    op.execute(
        """
        UPDATE recipe
        SET favorites_count = counts.total
        FROM (
            SELECT recipe_id, COUNT(*) AS total
            FROM favorite
            GROUP BY recipe_id
        ) AS counts
        WHERE recipe.id = counts.recipe_id
        """
    )


def downgrade() -> None:
    op.drop_column("recipe", "favorites_count")
