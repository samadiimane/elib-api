from __future__ import annotations

import sqlalchemy as sa

from tests.conftest import run_upgrade


def test_migration_backfills_journal_links(alembic_engine) -> None:
    engine, config = alembic_engine

    # Upgrade to the revision immediately before the new migration.
    run_upgrade(engine, config, "4be3cc9b9329")

    with engine.begin() as conn:
        conn.execute(
            sa.text(
                "INSERT INTO journals (id, slug, name) VALUES "
                "(:id1, :slug1, :name1), (:id2, :slug2, :name2)"
            ),
            dict(
                id1=1,
                slug1="science-today",
                name1="Science Today",
                id2=2,
                slug2="medical-review",
                name2="Medical Review",
            ),
        )
        conn.execute(
            sa.text(
                "INSERT INTO categories (id, slug, name, kind, parent_id, description) VALUES "
                "(1, :slug1, :name1, 'journal', NULL, NULL), "
                "(2, :slug2, :name2, 'journal', NULL, NULL), "
                "(3, :slug3, :name3, 'journal', NULL, NULL)"
            ),
            dict(
                slug1="science-today",
                name1="Science Today",
                slug2="med-review-category",
                name2="Medical Review",
                slug3="no-match",
                name3="Orphan Journal",
            ),
        )

    # Apply the new migration.
    run_upgrade(engine, config, "head")

    with engine.connect() as conn:
        rows = conn.execute(
            sa.text(
                "SELECT slug, journal_id FROM categories "
                "WHERE slug IN (:slug1, :slug2, :slug3) ORDER BY slug"
            ),
            dict(slug1="science-today", slug2="med-review-category", slug3="no-match"),
        ).all()

    mapping = {slug: journal_id for slug, journal_id in rows}

    assert mapping["science-today"] == 1
    assert mapping["med-review-category"] == 2
    assert mapping["no-match"] is None
