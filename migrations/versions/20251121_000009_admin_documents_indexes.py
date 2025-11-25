"""Add indexes to speed up admin document listings.

Revision ID: 20251121_000009
Revises: 20251121_000008
Create Date: 2025-11-21 00:00:09.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20251121_000009"
down_revision: Union[str, Sequence[str], None] = "20251121_000008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

INDEX_DEFS = (
    ("ix_documents_lang", ["lang"]),
    ("ix_documents_created_at", ["created_at"]),
    ("ix_documents_primary_category_id", ["primary_category_id"]),
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {idx["name"] for idx in inspector.get_indexes("documents")}
    for name, columns in INDEX_DEFS:
        if name not in existing:
            op.create_index(name, "documents", columns)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {idx["name"] for idx in inspector.get_indexes("documents")}
    for name, _columns in INDEX_DEFS:
        if name in existing:
            op.drop_index(name, table_name="documents")
