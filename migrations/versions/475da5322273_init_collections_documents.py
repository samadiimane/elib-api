"""init collections & documents

Revision ID: 475da5322273
Revises: 
Create Date: 2025-10-09 10:02:58.482676

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "475da5322273"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Initial legacy schema with collections and documents."""
    op.create_table(
        "collections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        "ix_collections_name",
        "collections",
        ["name"],
        unique=True,
    )

    op.create_table(
        "legacy_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("authors", sa.String(length=500), nullable=True),
        sa.Column("lang", sa.String(length=10), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("doi", sa.String(length=100), nullable=True),
        sa.Column("isbn", sa.String(length=50), nullable=True),
        sa.Column("issn", sa.String(length=50), nullable=True),
        sa.Column("pages", sa.Integer(), nullable=True),
        sa.Column("abstract", sa.Text(), nullable=True),
        sa.Column("file_key", sa.String(length=500), nullable=True),
        sa.Column("collection_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["collection_id"],
            ["collections.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_legacy_documents_title",
        "legacy_documents",
        ["title"],
        unique=False,
    )


def downgrade() -> None:
    """Drop legacy schema."""
    op.drop_index("ix_legacy_documents_title", table_name="legacy_documents")
    op.drop_table("legacy_documents")

    op.drop_index("ix_collections_name", table_name="collections")
    op.drop_table("collections")
