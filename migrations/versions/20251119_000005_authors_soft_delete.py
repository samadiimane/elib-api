"""Add soft delete column on authors

Revision ID: 20251119_000005
Revises: 20251119_000004
Create Date: 2025-11-19 20:05:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20251119_000005"
down_revision: Union[str, Sequence[str], None] = "20251119_000004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "authors",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("authors", "deleted_at")
