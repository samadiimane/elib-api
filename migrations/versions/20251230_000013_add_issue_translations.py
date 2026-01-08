"""Add issue translations table.

Revision ID: 20251230_000013
Revises: 20251230_000012
Create Date: 2025-12-30 00:00:13.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20251230_000013"
down_revision: Union[str, Sequence[str], None] = "20251230_000012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "issue_translations",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("issue_id", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(length=10), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["issue_id"], ["journal_issues.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("issue_id", "locale", name="uq_issue_translations_issue_locale"),
    )
    op.create_index("ix_issue_translations_issue_id", "issue_translations", ["issue_id"])
    op.create_index("ix_issue_translations_locale", "issue_translations", ["locale"])


def downgrade() -> None:
    op.drop_index("ix_issue_translations_locale", table_name="issue_translations")
    op.drop_index("ix_issue_translations_issue_id", table_name="issue_translations")
    op.drop_table("issue_translations")
