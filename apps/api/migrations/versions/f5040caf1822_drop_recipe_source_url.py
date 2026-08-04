"""drop recipe source_url

Recipes no longer carry outbound links. See PRODUCT.md: the product is the food
you cook, not a pointer somewhere else.

Destructive on purpose. `downgrade` restores the nullable column but cannot
restore any values that were in it — the data is gone once this runs forward.

Revision ID: f5040caf1822
Revises: 483043e64f00
Create Date: 2026-08-04 14:13:51.319062
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f5040caf1822"
down_revision: str | None = "483043e64f00"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("recipe", "source_url")


def downgrade() -> None:
    op.add_column(
        "recipe",
        sa.Column("source_url", sa.VARCHAR(length=500), autoincrement=False, nullable=True),
    )
