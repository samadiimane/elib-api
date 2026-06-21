"""journals: add journals and issues, link documents

Revision ID: 4be3cc9b9329
Revises: 3f1c2d9a4b5e
Create Date: 2025-10-22 12:39:17.433731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4be3cc9b9329'
down_revision: Union[str, Sequence[str], None] = '3f1c2d9a4b5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "journals",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("issn", sa.String(length=50), nullable=True),
        sa.Column("publisher", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_journals_name", "journals", ["name"])

    op.create_table(
        "journal_issues",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("journal_id", sa.Integer(), nullable=False),
        sa.Column("volume", sa.Integer(), nullable=True),
        sa.Column("number", sa.Integer(), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("issue_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["journal_id"], ["journals.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_journal_issues_journal_id", "journal_issues", ["journal_id"])
    op.create_index("ix_journal_issues_year", "journal_issues", ["year"])

    # Documents links
    op.add_column("documents", sa.Column("journal_id", sa.Integer(), nullable=True))
    op.add_column("documents", sa.Column("issue_id", sa.Integer(), nullable=True))
    op.add_column("documents", sa.Column("start_page", sa.Integer(), nullable=True))
    op.add_column("documents", sa.Column("end_page", sa.Integer(), nullable=True))

    op.create_index("ix_documents_journal_id", "documents", ["journal_id"])
    op.create_index("ix_documents_issue_id", "documents", ["issue_id"])

    # Add FKs only on DBs that support ALTER ADD CONSTRAINT well (Postgres)
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        op.create_foreign_key("fk_documents_journal", "documents", "journals",
                              ["journal_id"], ["id"], ondelete="SET NULL")
        op.create_foreign_key("fk_documents_issue", "documents", "journal_issues",
                              ["issue_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name != "sqlite":
        op.drop_constraint("fk_documents_issue", "documents", type_="foreignkey")
        op.drop_constraint("fk_documents_journal", "documents", type_="foreignkey")

    op.drop_index("ix_documents_issue_id", table_name="documents")
    op.drop_index("ix_documents_journal_id", table_name="documents")
    op.drop_column("documents", "end_page")
    op.drop_column("documents", "start_page")
    op.drop_column("documents", "issue_id")
    op.drop_column("documents", "journal_id")

    op.drop_index("ix_journal_issues_year", table_name="journal_issues")
    op.drop_index("ix_journal_issues_journal_id", table_name="journal_issues")
    op.drop_table("journal_issues")

    op.drop_index("ix_journals_name", table_name="journals")
    op.drop_table("journals")