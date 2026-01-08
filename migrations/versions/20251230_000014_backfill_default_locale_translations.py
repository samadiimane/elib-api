"""Backfill default-locale translations for journals and issues.

Revision ID: 20251230_000014
Revises: 20251230_000013
Create Date: 2025-12-30 00:00:14.000000
"""

from __future__ import annotations

import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20251230_000014"
down_revision: Union[str, Sequence[str], None] = "20251230_000013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _default_locale() -> str:
    """Resolve DEFAULT_LOCALE env (fallback to en) and normalize to lowercase."""
    return (os.getenv("DEFAULT_LOCALE") or "en").strip().lower()


def upgrade() -> None:
    locale = _default_locale()
    # Journals: backfill name/description/publisher
    op.execute(
        sa.text(
            """
            INSERT INTO journal_translations (journal_id, locale, title, description, publisher)
            SELECT j.id, :locale, j.name, j.description, j.publisher
            FROM journals j
            WHERE NOT EXISTS (
                SELECT 1 FROM journal_translations jt
                WHERE jt.journal_id = j.id AND jt.locale = :locale
            )
            """
        ).bindparams(locale=locale)
    )

    # Issues: backfill title only when present (description is NULL)
    op.execute(
        sa.text(
            """
            INSERT INTO issue_translations (issue_id, locale, title, description)
            SELECT i.id, :locale, i.title, NULL
            FROM journal_issues i
            WHERE i.title IS NOT NULL
              AND NOT EXISTS (
                SELECT 1 FROM issue_translations it
                WHERE it.issue_id = i.id AND it.locale = :locale
              )
            """
        ).bindparams(locale=locale)
    )


def downgrade() -> None:
    locale = _default_locale()
    op.execute(sa.text("DELETE FROM issue_translations WHERE locale = :locale").bindparams(locale=locale))
    op.execute(sa.text("DELETE FROM journal_translations WHERE locale = :locale").bindparams(locale=locale))
