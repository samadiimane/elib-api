"""Add foundational auth tables."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import expression


revision = "4fbfbbb0f7af"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=expression.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    auth_provider_enum = sa.Enum(
        "password",
        "google",
        name="auth_provider",
        native_enum=False,
    )
    user_role_enum = sa.Enum(
        "researcher",
        "committee",
        "admin",
        name="user_role",
        native_enum=False,
    )
    op.create_table(
        "auth_identities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", auth_provider_enum, nullable=False),
        sa.Column("provider_user_id", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint(
            "provider",
            "provider_user_id",
            name="uq_auth_identities_provider_user",
        ),
    )
    op.create_index("ix_auth_identities_user_id", "auth_identities", ["user_id"])

    op.create_table(
        "user_roles",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", user_role_enum, nullable=False),
        sa.PrimaryKeyConstraint("user_id", "role", name="pk_user_roles"),
    )
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_roles_user_id", table_name="user_roles")
    op.drop_table("user_roles")

    op.drop_index("ix_auth_identities_user_id", table_name="auth_identities")
    op.drop_table("auth_identities")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    # No dedicated enum types to drop when native_enum=False.
