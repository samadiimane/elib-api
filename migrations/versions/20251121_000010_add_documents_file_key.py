"""Add file_key to documents for admin uploads.

Revision ID: 20251121_000010
Revises: 20251121_000009
Create Date: 2025-11-21 00:00:10.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20251121_000010"
down_revision: Union[str, Sequence[str], None] = "20251121_000009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("file_key", sa.String(length=500), nullable=True))
    op.create_index("ix_documents_file_key", "documents", ["file_key"])


def downgrade() -> None:
    op.drop_index("ix_documents_file_key", table_name="documents")
    op.drop_column("documents", "file_key")
