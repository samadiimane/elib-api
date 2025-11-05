"""Introduce authors and document cover image support.

Revision ID: 20251101_000001
Revises: 20251024_000001
Create Date: 2025-11-01 00:00:01.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20251101_000001"
down_revision: Union[str, Sequence[str], None] = "20251024_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


AUTHOR_TABLE_NAME = "authors"
DOCUMENT_AUTHORS_TABLE_NAME = "document_authors"


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return inspector.has_table(table_name)


def _column_exists(inspector: sa.Inspector, table: str, column: str) -> bool:
    return any(col["name"] == column for col in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, AUTHOR_TABLE_NAME):
        op.create_table(
            AUTHOR_TABLE_NAME,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("full_name_ar", sa.String(length=255), nullable=False),
            sa.Column("full_name_lat", sa.String(length=255), nullable=True),
            sa.Column("affiliation", sa.String(length=255), nullable=True),
            sa.Column("slug", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint("slug", name="uq_authors_slug"),
        )

    if not _table_exists(inspector, DOCUMENT_AUTHORS_TABLE_NAME):
        op.create_table(
            DOCUMENT_AUTHORS_TABLE_NAME,
            sa.Column("document_id", sa.Integer(), nullable=False),
            sa.Column("author_id", sa.Integer(), nullable=False),
            sa.Column("position", sa.Integer(), nullable=False, server_default=sa.text("1")),
            sa.ForeignKeyConstraint(
                ["document_id"],
                ["documents.id"],
                ondelete="CASCADE",
                name="fk_document_authors_document",
            ),
            sa.ForeignKeyConstraint(
                ["author_id"],
                [f"{AUTHOR_TABLE_NAME}.id"],
                ondelete="CASCADE",
                name="fk_document_authors_author",
            ),
            sa.PrimaryKeyConstraint("document_id", "author_id", name="pk_document_authors"),
        )
        op.create_index(
            "ix_document_authors_document_position",
            DOCUMENT_AUTHORS_TABLE_NAME,
            ["document_id", "position"],
        )

    if not _column_exists(inspector, "documents", "cover_image_url"):
        if bind.dialect.name == "sqlite":
            with op.batch_alter_table("documents", recreate="always") as batch_op:
                batch_op.add_column(sa.Column("cover_image_url", sa.String(length=500), nullable=True))
        else:
            op.add_column("documents", sa.Column("cover_image_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if bind.dialect.name == "sqlite":
        if _column_exists(inspector, "documents", "cover_image_url"):
            with op.batch_alter_table("documents", recreate="always") as batch_op:
                batch_op.drop_column("cover_image_url")
    else:
        if _column_exists(inspector, "documents", "cover_image_url"):
            op.drop_column("documents", "cover_image_url")

    if _table_exists(inspector, DOCUMENT_AUTHORS_TABLE_NAME):
        idx_names = {idx["name"] for idx in inspector.get_indexes(DOCUMENT_AUTHORS_TABLE_NAME)}
        if "ix_document_authors_document_position" in idx_names:
            op.drop_index("ix_document_authors_document_position", table_name=DOCUMENT_AUTHORS_TABLE_NAME)
        op.drop_table(DOCUMENT_AUTHORS_TABLE_NAME)

    if _table_exists(inspector, AUTHOR_TABLE_NAME):
        op.drop_table(AUTHOR_TABLE_NAME)
