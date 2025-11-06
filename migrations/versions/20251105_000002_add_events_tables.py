"""Add events tables for seminars, awards, and exhibitions.

Revision ID: 20251105_000002
Revises: 20251101_000001
Create Date: 2025-11-05 00:00:02.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20251105_000002"
down_revision: Union[str, Sequence[str], None] = "20251101_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("cover_image_url", sa.String(length=1024), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "type in ('seminar', 'award', 'exhibition')",
            name="ck_events_type_valid",
        ),
    )
    op.create_index("ix_events_slug", "events", ["slug"], unique=True)
    op.create_index("ix_events_type", "events", ["type"], unique=False)

    op.create_table(
        "seminar_events",
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("speakers_json", sa.JSON(), nullable=True),
        sa.Column("agenda_json", sa.JSON(), nullable=True),
        sa.Column("media_json", sa.JSON(), nullable=True),
    )

    op.create_table(
        "award_events",
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("award_year", sa.Integer(), nullable=True),
        sa.Column("discipline", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    op.create_table(
        "exhibition_events",
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("venue", sa.String(length=255), nullable=True),
        sa.Column("gallery_json", sa.JSON(), nullable=True),
        sa.Column("curator", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "award_event_winners",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("winner_name", sa.String(length=255), nullable=False),
        sa.Column("work_title", sa.String(length=255), nullable=True),
        sa.Column("affiliation", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_award_event_winners_event_id", "award_event_winners", ["event_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_award_event_winners_event_id", table_name="award_event_winners")
    op.drop_table("award_event_winners")
    op.drop_table("exhibition_events")
    op.drop_table("award_events")
    op.drop_table("seminar_events")
    op.drop_index("ix_events_type", table_name="events")
    op.drop_index("ix_events_slug", table_name="events")
    op.drop_table("events")
