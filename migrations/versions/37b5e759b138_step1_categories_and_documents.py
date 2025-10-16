"""step1: categories and documents

Revision ID: 37b5e759b138
Revises: 475da5322273
Create Date: 2025-10-16 12:05:20.906638

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "37b5e759b138"
down_revision: Union[str, Sequence[str], None] = "475da5322273"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ENUM_VALUES_CATEGORY = ("section", "journal", "archive_collection", "topic")
ENUM_VALUES_DOCUMENT = (
    "book",
    "article",
    "thesis",
    "report",
    "manuscript",
    "archive_item",
    "site_record",
    "other",
)


def _enum_types(bind):
    if bind.dialect.name == "postgresql":
        category_enum = sa.Enum(
            *ENUM_VALUES_CATEGORY,
            name="category_kind",
            create_type=False,
        )
        document_enum = sa.Enum(
            *ENUM_VALUES_DOCUMENT,
            name="doc_type",
            create_type=False,
        )
    else:
        category_enum = sa.Enum(
            *ENUM_VALUES_CATEGORY,
            name="category_kind",
            native_enum=False,
        )
        document_enum = sa.Enum(
            *ENUM_VALUES_DOCUMENT,
            name="doc_type",
            native_enum=False,
        )
    return category_enum, document_enum


def upgrade() -> None:
    """Upgrade schema with canonical categories/documents."""
    bind = op.get_bind()
    inspector = inspect(bind)

    category_enum, document_enum = _enum_types(bind)

    if bind.dialect.name == "postgresql":
        op.execute(
            "CREATE TYPE IF NOT EXISTS category_kind "
            "AS ENUM ('section','journal','archive_collection','topic');"
        )
        op.execute(
            "CREATE TYPE IF NOT EXISTS doc_type "
            "AS ENUM ('book','article','thesis','report','manuscript','archive_item','site_record','other');"
        )

    if inspector.has_table("documents") and not inspector.has_table("legacy_documents"):
        op.rename_table("documents", "legacy_documents")

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("kind", category_enum, nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["categories.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_categories_kind", "categories", ["kind"], unique=False)
    op.create_index(
        "ix_categories_parent_id",
        "categories",
        ["parent_id"],
        unique=False,
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("abstract", sa.Text(), nullable=True),
        sa.Column("type", document_enum, nullable=False),
        sa.Column("lang", sa.String(length=10), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("pages", sa.Integer(), nullable=True),
        sa.Column("doi", sa.String(length=100), nullable=True),
        sa.Column("isbn", sa.String(length=50), nullable=True),
        sa.Column("issn", sa.String(length=50), nullable=True),
        sa.Column("primary_category_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["primary_category_id"],
            ["categories.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_type", "documents", ["type"], unique=False)
    op.create_index("ix_documents_year", "documents", ["year"], unique=False)


def downgrade() -> None:
    """Downgrade schema to legacy-only."""
    op.drop_index("ix_documents_year", table_name="documents")
    op.drop_index("ix_documents_type", table_name="documents")
    op.drop_table("documents")

    op.drop_index("ix_categories_parent_id", table_name="categories")
    op.drop_index("ix_categories_kind", table_name="categories")
    op.drop_table("categories")

    bind = op.get_bind()
    inspector = inspect(bind)

    if inspector.has_table("legacy_documents") and not inspector.has_table("documents"):
        op.rename_table("legacy_documents", "documents")

    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS doc_type;")
        op.execute("DROP TYPE IF EXISTS category_kind;")
