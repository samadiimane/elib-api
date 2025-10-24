"""Add categories.journal_id links journals to navigation categories.

Revision ID: 20251024_000001
Revises: 4be3cc9b9329
Create Date: 2025-10-24 00:00:01.000000
"""

from __future__ import annotations

import logging
import re
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm, select


# revision identifiers, used by Alembic.
revision: str = "20251024_000001"
down_revision: Union[str, Sequence[str], None] = "4be3cc9b9329"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(inspector: sa.Inspector, table: str, column: str) -> bool:
    return any(col["name"] == column for col in inspector.get_columns(table))


def _normalize(text: str) -> str:
    base = text.strip().lower()
    # Treat spaces and hyphens equivalently for loose name matching.
    collapsed = re.sub(r"[\s\-]+", "-", base)
    return collapsed


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    logger = logging.getLogger("alembic.runtime.migration")

    if not _column_exists(inspector, "categories", "journal_id"):
        if bind.dialect.name == "sqlite":
            with op.batch_alter_table("categories", recreate="always") as batch_op:
                batch_op.add_column(sa.Column("journal_id", sa.Integer(), nullable=True))
                batch_op.create_foreign_key(
                    "fk_categories_journal",
                    "journals",
                    ["journal_id"],
                    ["id"],
                    ondelete="SET NULL",
                )
        else:
            op.add_column("categories", sa.Column("journal_id", sa.Integer(), nullable=True))
            op.create_foreign_key(
                "fk_categories_journal",
                "categories",
                "journals",
                ["journal_id"],
                ["id"],
                ondelete="SET NULL",
                ifnotexists=True,
            )

    categories_table = sa.Table(
        "categories",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("slug", sa.String(100)),
        sa.Column("name", sa.String(255)),
        sa.Column("kind", sa.String(50)),
        sa.Column("journal_id", sa.Integer),
    )
    journals_table = sa.Table(
        "journals",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("slug", sa.String(100)),
        sa.Column("name", sa.String(255)),
    )

    with orm.Session(bind=bind) as session:
        journal_rows = session.execute(
            select(
                journals_table.c.id,
                journals_table.c.slug,
                journals_table.c.name,
            )
        ).all()
        journal_by_slug = {row.slug: row.id for row in journal_rows}
        journal_by_name = {_normalize(row.name): row.id for row in journal_rows if row.name}

        unresolved: list[tuple[int, str]] = []
        updated = False

        category_rows = session.execute(
            select(
                categories_table.c.id,
                categories_table.c.slug,
                categories_table.c.name,
            )
            .where(categories_table.c.kind == "journal")
            .where(categories_table.c.journal_id.is_(None))
        ).all()

        for row in category_rows:
            match_id = journal_by_slug.get(row.slug)
            if match_id is None and row.name:
                match_id = journal_by_name.get(_normalize(row.name))

            if match_id is None:
                unresolved.append((row.id, row.slug))
                continue

            session.execute(
                categories_table.update()
                .where(categories_table.c.id == row.id)
                .values(journal_id=match_id)
            )
            updated = True

        if unresolved:
            for cat_id, slug in unresolved:
                logger.info(
                    "categories.journal_id backfill unresolved",
                    extra={"category_id": cat_id, "slug": slug},
                )

        if updated:
            session.commit()

    if bind.dialect.name != "sqlite":
        existing_constraints = {
            constraint["name"]: constraint
            for constraint in inspector.get_unique_constraints("journals")
        }
        slug_unique_exists = any(
            set(constraint["column_names"]) == {"slug"}
            for constraint in existing_constraints.values()
        )
        if not slug_unique_exists:
            op.create_unique_constraint("uq_journals_slug", "journals", ["slug"])

        issue_constraints = inspector.get_unique_constraints("journal_issues")
        desired_cols = {"journal_id", "year", "volume", "number"}
        has_issue_unique = any(set(constraint["column_names"]) == desired_cols for constraint in issue_constraints)
        if not has_issue_unique:
            op.create_unique_constraint(
                "uq_journal_issues_identity",
                "journal_issues",
                ["journal_id", "year", "volume", "number"],
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if bind.dialect.name != "sqlite":
        issue_constraints = {c["name"] for c in inspector.get_unique_constraints("journal_issues")}
        if "uq_journal_issues_identity" in issue_constraints:
            op.drop_constraint("uq_journal_issues_identity", "journal_issues", type_="unique")

        journal_constraints = {c["name"] for c in inspector.get_unique_constraints("journals")}
        if "uq_journals_slug" in journal_constraints:
            op.drop_constraint("uq_journals_slug", "journals", type_="unique")

        category_fks = {fk["name"] for fk in inspector.get_foreign_keys("categories")}
        if "fk_categories_journal" in category_fks:
            op.drop_constraint("fk_categories_journal", "categories", type_="foreignkey")

        if _column_exists(inspector, "categories", "journal_id"):
            op.drop_column("categories", "journal_id")
    else:
        with op.batch_alter_table("categories", recreate="always") as batch_op:
            fks = {fk["name"] for fk in inspector.get_foreign_keys("categories")}
            if "fk_categories_journal" in fks:
                batch_op.drop_constraint("fk_categories_journal", type_="foreignkey")
            if _column_exists(inspector, "categories", "journal_id"):
                batch_op.drop_column("journal_id")
