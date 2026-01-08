"""Add journal translations table.

Revision ID: 20251230_000012
Revises: 20251121_000011
Create Date: 2025-12-30 00:00:12.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20251230_000012"
down_revision: Union[str, Sequence[str], None] = "20251121_000011_documents_soft_delete"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "journal_translations",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("journal_id", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(length=10), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("publisher", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["journal_id"], ["journals.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("journal_id", "locale", name="uq_journal_translations_journal_locale"),
        sa.CheckConstraint("lower(locale) = locale", name="ck_journal_translations_locale_lower"),
    )
    op.create_index("ix_journal_translations_journal_id", "journal_translations", ["journal_id"])
    op.create_index("ix_journal_translations_locale", "journal_translations", ["locale"])


def downgrade() -> None:
    op.drop_index("ix_journal_translations_locale", table_name="journal_translations")
    op.drop_index("ix_journal_translations_journal_id", table_name="journal_translations")
    op.drop_table("journal_translations")
