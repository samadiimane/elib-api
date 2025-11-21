"""Enhance journals with cover images, soft delete, and indexes.

Revision ID: 20251120_000006
Revises: 20251119_000005
Create Date: 2025-11-20 00:00:06.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20251120_000006"
down_revision: Union[str, Sequence[str], None] = "20251119_000005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JOURNALS_TABLE = "journals"
SQLITE_OLD_TABLE = "journals__old"
PARTIAL_UNIQUE_NAME = "uq_journals_slug_active"


def _column_exists(inspector: sa.Inspector, table: str, column: str) -> bool:
    return any(col["name"] == column for col in inspector.get_columns(table))


def _index_exists(inspector: sa.Inspector, table: str, index_name: str) -> bool:
    return any(idx["name"] == index_name for idx in inspector.get_indexes(table))


def _slug_unique_constraint(inspector: sa.Inspector) -> str | None:
    for constraint in inspector.get_unique_constraints(JOURNALS_TABLE):
        columns = constraint.get("column_names") or []
        if len(columns) == 1 and columns[0] == "slug":
            return constraint["name"]
    return None


def _create_indexes(bind: sa.engine.Connection, inspector: sa.Inspector) -> None:
    idx_names = {idx["name"] for idx in inspector.get_indexes(JOURNALS_TABLE)}
    if "ix_journals_name" not in idx_names:
        op.create_index("ix_journals_name", JOURNALS_TABLE, ["name"])
    if "ix_journals_slug" not in idx_names:
        op.create_index("ix_journals_slug", JOURNALS_TABLE, ["slug"])
    if "ix_journals_created_at" not in idx_names:
        op.create_index("ix_journals_created_at", JOURNALS_TABLE, ["created_at"])
    if "ix_journals_deleted_at" not in idx_names:
        op.create_index("ix_journals_deleted_at", JOURNALS_TABLE, ["deleted_at"])

    if bind.dialect.name == "postgresql":
        if PARTIAL_UNIQUE_NAME not in idx_names:
            op.create_index(
                PARTIAL_UNIQUE_NAME,
                JOURNALS_TABLE,
                ["slug"],
                unique=True,
                postgresql_where=sa.text("deleted_at IS NULL"),
            )


def _upgrade_sqlite(bind: sa.engine.Connection, inspector: sa.Inspector) -> None:
    existing_columns = {col["name"] for col in inspector.get_columns(JOURNALS_TABLE)}

    op.execute("PRAGMA foreign_keys=OFF")
    op.rename_table(JOURNALS_TABLE, SQLITE_OLD_TABLE)

    op.create_table(
        JOURNALS_TABLE,
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("issn", sa.String(length=50), nullable=True),
        sa.Column("publisher", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cover_image_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    selectable_columns: list[str] = []
    for column in [
        "id",
        "slug",
        "name",
        "issn",
        "publisher",
        "description",
        "cover_image_url",
        "created_at",
        "updated_at",
        "deleted_at",
    ]:
        if column in existing_columns:
            selectable_columns.append(column)
        elif column == "cover_image_url":
            selectable_columns.append("NULL AS cover_image_url")
        elif column == "deleted_at":
            selectable_columns.append("NULL AS deleted_at")
        else:
            raise RuntimeError(f"Missing required column '{column}' in existing journals table")

    op.execute(
        sa.text(
            f"""
            INSERT INTO {JOURNALS_TABLE} (
                id, slug, name, issn, publisher, description,
                cover_image_url, created_at, updated_at, deleted_at
            )
            SELECT {", ".join(selectable_columns)}
            FROM {SQLITE_OLD_TABLE}
            """
        )
    )
    op.drop_table(SQLITE_OLD_TABLE)
    op.execute("PRAGMA foreign_keys=ON")


def _upgrade_default(bind: sa.engine.Connection, inspector: sa.Inspector) -> None:
    if not _column_exists(inspector, JOURNALS_TABLE, "cover_image_url"):
        op.add_column(JOURNALS_TABLE, sa.Column("cover_image_url", sa.String(length=500), nullable=True))
    if not _column_exists(inspector, JOURNALS_TABLE, "deleted_at"):
        op.add_column(JOURNALS_TABLE, sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    constraint_name = _slug_unique_constraint(inspector)
    if constraint_name:
        op.drop_constraint(constraint_name, JOURNALS_TABLE, type_="unique")


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if bind.dialect.name == "sqlite":
        _upgrade_sqlite(bind, inspector)
    else:
        _upgrade_default(bind, inspector)

    inspector = sa.inspect(bind)
    _create_indexes(bind, inspector)


def _drop_index_if_exists(inspector: sa.Inspector, name: str) -> None:
    if _index_exists(inspector, JOURNALS_TABLE, name):
        op.drop_index(name, table_name=JOURNALS_TABLE)


def _downgrade_sqlite(bind: sa.engine.Connection, inspector: sa.Inspector) -> None:
    op.execute("PRAGMA foreign_keys=OFF")
    op.rename_table(JOURNALS_TABLE, SQLITE_OLD_TABLE)

    op.create_table(
        JOURNALS_TABLE,
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("issn", sa.String(length=50), nullable=True),
        sa.Column("publisher", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_journals_name", JOURNALS_TABLE, ["name"])

    op.execute(
        sa.text(
            f"""
            INSERT INTO {JOURNALS_TABLE} (
                id, slug, name, issn, publisher, description, created_at, updated_at
            )
            SELECT id, slug, name, issn, publisher, description, created_at, updated_at
            FROM {SQLITE_OLD_TABLE}
            """
        )
    )

    op.drop_table(SQLITE_OLD_TABLE)
    op.execute("PRAGMA foreign_keys=ON")


def _downgrade_default(bind: sa.engine.Connection, inspector: sa.Inspector) -> None:
    _drop_index_if_exists(inspector, PARTIAL_UNIQUE_NAME)
    _drop_index_if_exists(inspector, "ix_journals_slug")
    _drop_index_if_exists(inspector, "ix_journals_created_at")
    _drop_index_if_exists(inspector, "ix_journals_deleted_at")

    if _column_exists(inspector, JOURNALS_TABLE, "cover_image_url"):
        op.drop_column(JOURNALS_TABLE, "cover_image_url")
    if _column_exists(inspector, JOURNALS_TABLE, "deleted_at"):
        op.drop_column(JOURNALS_TABLE, "deleted_at")

    op.create_unique_constraint("uq_journals_slug", JOURNALS_TABLE, ["slug"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if bind.dialect.name == "sqlite":
        _downgrade_sqlite(bind, inspector)
    else:
        _downgrade_default(bind, inspector)
