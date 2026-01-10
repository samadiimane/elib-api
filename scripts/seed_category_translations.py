"""
Seed category translations (en/fr/es/ar) for key archive-related categories.

Usage:
    python scripts/seed_category_translations.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Mapping

import sqlalchemy as sa
from sqlalchemy.orm import Session

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.session import engine  # noqa: E402


ARCHIVE_TRANSLATIONS: Mapping[str, Mapping[str, dict[str, str | None]]] = {
    "archives": {
        "fr": {"title": "Archives et patrimoine documentaire", "description": None},
        "es": {"title": "Archivos y patrimonio documental", "description": None},
        "ar": {"title": "الأرشيف والرصيد الوثائقي", "description": None},
    },
    "manuscript": {
        "fr": {
            "title": "Guide des collections de manuscrits",
            "description": "Instruments de recherche, catalogues et inventaires des fonds de manuscrits.",
        },
        "es": {
            "title": "Guía de colecciones de manuscritos",
            "description": "Instrumentos de búsqueda, catálogos e inventarios de fondos manuscritos.",
        },
        "ar": {
            "title": "دليل مجموعات المخطوطات",
            "description": "أدوات البحث، الفهارس والجرد لمجموعات المخطوطات.",
        },
    },
    "municipal-ledgers": {
        "fr": {
            "title": "Registres municipaux",
            "description": "Délibérations des conseils urbains, rôles fiscaux et registres comptables de la vie municipale.",
        },
        "es": {
            "title": "Libros de cuentas municipales",
            "description": "Actas de consejos urbanos, padrones fiscales y libros contables de la vida municipal.",
        },
        "ar": {
            "title": "السجلات البلدية",
            "description": "محاضر المجالس الحضرية، سجلات الضرائب ودفاتر الحسابات التي توثق الحياة البلدية.",
        },
    },
    "protectorate-records": {
        "fr": {
            "title": "Archives du Protectorat",
            "description": "Correspondances, bulletins et dossiers produits par les administrations coloniales et les services du Protectorat.",
        },
        "es": {
            "title": "Registros del Protectorado",
            "description": "Correspondencia, boletines y expedientes generados por las administraciones coloniales y oficinas del Protectorado.",
        },
        "ar": {
            "title": "سجلات الحماية",
            "description": "مراسلات ونشرات وملفات صادرة عن الإدارات الاستعمارية ومصالح الحماية.",
        },
    },
}


def fetch_categories(session: Session) -> dict[str, tuple[int, str | None, str | None]]:
    rows = session.execute(
        sa.text("SELECT id, slug, name, description FROM categories")
    ).mappings()
    return {
        row["slug"]: (row["id"], row.get("name"), row.get("description"))
        for row in rows
    }


def upsert_translation(session: Session, category_id: int, locale: str, title: str, description: str | None) -> None:
    stmt = sa.text(
        """
        INSERT INTO category_translations (category_id, locale, title, description)
        VALUES (:category_id, :locale, :title, :description)
        ON CONFLICT(category_id, locale) DO UPDATE
        SET title = excluded.title, description = excluded.description
        """
    )
    session.execute(
        stmt,
        {
            "category_id": category_id,
            "locale": locale,
            "title": title,
            "description": description,
        },
    )


def seed(session: Session) -> None:
    categories = fetch_categories(session)

    # Seed default English translations from base fields
    for slug, (category_id, name, desc) in categories.items():
        title = (name or "").strip()
        description = (desc or None)
        if title:
            upsert_translation(session, category_id, "en", title, description)

    # Seed curated fr/es/ar translations for specific slugs
    for slug, locales in ARCHIVE_TRANSLATIONS.items():
        if slug not in categories:
            continue
        category_id, _, _ = categories[slug]
        for locale, payload in locales.items():
            title = payload.get("title")
            desc = payload.get("description")
            if title:
                upsert_translation(session, category_id, locale, title, desc)


def main() -> None:
    with Session(engine) as session:
        with session.begin():
            seed(session)
    print("Category translations seeded.")


if __name__ == "__main__":
    main()
