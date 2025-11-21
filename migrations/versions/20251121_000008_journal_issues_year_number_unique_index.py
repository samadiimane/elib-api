"""Add composite index on journal issues (journal_id, year, number).

Revision ID: 20251121_000008
Revises: 20251121_000007
Create Date: 2025-11-21 00:00:08.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20251121_000008"
down_revision: Union[str, Sequence[str], None] = "20251121_000007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {idx["name"] for idx in inspector.get_indexes("journal_issues")}
    if "ix_journal_issues_journal_year_number" not in existing:
        op.create_index(
            "ix_journal_issues_journal_year_number",
            "journal_issues",
            ["journal_id", "year", "number"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {idx["name"] for idx in inspector.get_indexes("journal_issues")}
    if "ix_journal_issues_journal_year_number" in existing:
        op.drop_index("ix_journal_issues_journal_year_number", table_name="journal_issues")
