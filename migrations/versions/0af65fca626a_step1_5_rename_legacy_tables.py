"""step1_5: rename legacy tables

Revision ID: 0af65fca626a
Revises: ef1a76713e76
Create Date: 2025-10-16 13:15:28.094568

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0af65fca626a"
down_revision: Union[str, Sequence[str], None] = "ef1a76713e76"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _rename_if_exists(old: str, new: str) -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    if old in tables and new not in tables:
        op.rename_table(old, new)


def upgrade() -> None:
    """Upgrade schema by renaming legacy tables."""
    _rename_if_exists("collections", "collections_legacy")
    _rename_if_exists("legacy_documents", "legacy_documents_legacy")


def downgrade() -> None:
    """Downgrade schema by restoring original legacy table names."""
    _rename_if_exists("collections_legacy", "collections")
    _rename_if_exists("legacy_documents_legacy", "legacy_documents")
