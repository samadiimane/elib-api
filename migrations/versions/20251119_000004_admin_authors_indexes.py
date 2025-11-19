"""Add author indexes for search performance

Revision ID: 20251119_000004
Revises: 20251119_000003
Create Date: 2025-11-19 18:45:00.000000
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20251119_000004"
down_revision: Union[str, Sequence[str], None] = "20251119_000003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_authors_full_name_lat", "authors", ["full_name_lat"], unique=False)
    op.create_index("ix_authors_created_at", "authors", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_authors_created_at", table_name="authors")
    op.drop_index("ix_authors_full_name_lat", table_name="authors")
