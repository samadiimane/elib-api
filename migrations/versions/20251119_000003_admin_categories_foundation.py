"""Admin category metadata enhancements

Revision ID: 20251119_000003
Revises: b10c8c8d8bc2
Create Date: 2025-11-19 12:15:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "20251119_000003"
down_revision: Union[str, Sequence[str], None] = "b10c8c8d8bc2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _drop_unique_slug_constraint() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    slug_constraint = next(
        (
            constraint["name"]
            for constraint in inspector.get_unique_constraints("categories")
            if constraint.get("column_names") == ["slug"]
        ),
        None,
    )
    if not slug_constraint:
        return
    with op.batch_alter_table("categories") as batch_op:
        batch_op.drop_constraint(slug_constraint, type_="unique")


def upgrade() -> None:
    _drop_unique_slug_constraint()
    with op.batch_alter_table("categories") as batch_op:
        batch_op.add_column(
            sa.Column("order_index", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            )
        )
        batch_op.create_unique_constraint(
            "uq_categories_kind_slug", ["kind", "slug"]
        )
        batch_op.create_index(
            "ix_categories_parent_order", ["parent_id", "order_index"]
        )
        batch_op.create_index("ix_categories_slug", ["slug"])


def downgrade() -> None:
    with op.batch_alter_table("categories") as batch_op:
        batch_op.drop_index("ix_categories_slug")
        batch_op.drop_index("ix_categories_parent_order")
        batch_op.drop_constraint("uq_categories_kind_slug", type_="unique")
        batch_op.drop_column("created_at")
        batch_op.drop_column("order_index")
        batch_op.create_unique_constraint("uq_categories_slug", ["slug"])
