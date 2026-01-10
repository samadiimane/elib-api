"""Add category translations table.

Revision ID: 20260105_000016
Revises: 20251230_000015
Create Date: 2026-01-05 00:00:16.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260105_000016"
down_revision: Union[str, Sequence[str], None] = "20251230_000015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "category_translations",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("locale", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("category_id", "locale", name="uq_category_translations_category_locale"),
        sa.CheckConstraint(
            "locale IN ('en','fr','es','ar')",
            name="ck_category_translations_locale_allowed",
        ),
    )
    op.create_index("ix_category_translations_category_id", "category_translations", ["category_id"])
    op.create_index(
        "ix_category_translations_locale_category_id",
        "category_translations",
        ["locale", "category_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_category_translations_locale_category_id", table_name="category_translations")
    op.drop_index("ix_category_translations_category_id", table_name="category_translations")
    op.drop_table("category_translations")
