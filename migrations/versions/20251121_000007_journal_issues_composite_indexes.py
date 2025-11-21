"""Add composite indexes on journal issues.

Revision ID: 20251121_000007
Revises: 20251120_000006
Create Date: 2025-11-21 00:00:07.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20251121_000007"
down_revision: Union[str, Sequence[str], None] = "20251120_000006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {idx["name"] for idx in inspector.get_indexes("journal_issues")}

    if "ix_journal_issues_journal_year" not in existing:
        op.create_index(
            "ix_journal_issues_journal_year",
            "journal_issues",
            ["journal_id", "year"],
        )
    if "ix_journal_issues_journal_number" not in existing:
        op.create_index(
            "ix_journal_issues_journal_number",
            "journal_issues",
            ["journal_id", "number"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {idx["name"] for idx in inspector.get_indexes("journal_issues")}

    if "ix_journal_issues_journal_number" in existing:
        op.drop_index("ix_journal_issues_journal_number", table_name="journal_issues")
    if "ix_journal_issues_journal_year" in existing:
        op.drop_index("ix_journal_issues_journal_year", table_name="journal_issues")
