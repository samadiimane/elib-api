"""add trigram indexes for document search

Revision ID: 3f1c2d9a4b5e
Revises: 02440c4b7c1e
Create Date: 2025-10-17 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "3f1c2d9a4b5e"
down_revision: Union[str, Sequence[str], None] = "02440c4b7c1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_documents_title_trgm "
        "ON documents USING gin (title gin_trgm_ops);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_documents_abstract_trgm "
        "ON documents USING gin (abstract gin_trgm_ops);"
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("DROP INDEX IF EXISTS ix_documents_abstract_trgm;")
    op.execute("DROP INDEX IF EXISTS ix_documents_title_trgm;")
