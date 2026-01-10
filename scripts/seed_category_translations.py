"""
Seed category translations (en/fr/es/ar) for archives and research themes.

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
    "research-themes": {
        "en": {"title": "Research Issues & Problematics", "description": "Cross-disciplinary questions shaping current research in the Maghreb."},
        "fr": {"title": "Probl\u00e9matiques et axes de recherche", "description": "Questions transdisciplinaires qui structurent la recherche au Maghreb."},
        "es": {"title": "Tem\u00e1ticas y problem\u00e1ticas de investigaci\u00f3n", "description": "Preguntas transdisciplinares que orientan la investigaci\u00f3n en el Magreb."},
        "ar": {"title": "\u0642\u0636\u0627\u064a\u0627 \u0648\u0625\u0634\u0643\u0627\u0644\u064a\u0627\u062a \u0627\u0644\u0628\u062d\u062b", "description": "\u0623\u0633\u0626\u0644\u0629 \u0639\u0627\u0628\u0631\u0629 \u0644\u0644\u062a\u062e\u0635\u0635\u0627\u062a \u062a\u0648\u062c\u0647 \u0627\u0644\u0628\u062d\u062b \u0641\u064a \u0627\u0644\u0645\u063a\u0631\u0628 \u0627\u0644\u0643\u0628\u064a\u0631."},
    },
    "urban-histories": {
        "en": {"title": "Urban Histories", "description": "Neighbourhoods, governance, and the rhythms of everyday urban life."},
        "fr": {"title": "Histoires urbaines", "description": "Quartiers, gouvernance et rythmes de la vie urbaine."},
        "es": {"title": "Historias urbanas", "description": "Barrios, gobernanza y ritmos de la vida cotidiana."},
        "ar": {"title": "\u062a\u0627\u0631\u064a\u062e \u0627\u0644\u0645\u062f\u0646", "description": "\u0627\u0644\u0623\u062d\u064a\u0627\u0621\u060c \u0627\u0644\u062d\u0648\u0643\u0645\u0629\u060c \u0648\u0625\u064a\u0642\u0627\u0639\u0627\u062a \u0627\u0644\u062d\u064a\u0627\u0629 \u0627\u0644\u064a\u0648\u0645\u064a\u0629."},
    },
    "material-culture": {
        "en": {"title": "Material Culture", "description": "Objects, artisanship, and museum practices across the Maghreb."},
        "fr": {"title": "Culture mat\u00e9rielle", "description": "Objets, artisanat et pratiques mus\u00e9ales au Maghreb."},
        "es": {"title": "Cultura material", "description": "Objetos, artesan\u00edas y pr\u00e1cticas muse\u00edsticas en el Magreb."},
        "ar": {"title": "\u0627\u0644\u062b\u0642\u0627\u0641\u0629 \u0627\u0644\u0645\u0627\u062f\u064a\u0629", "description": "\u0627\u0644\u0623\u0634\u064a\u0627\u0621 \u0648\u0627\u0644\u062d\u0631\u0641 \u0648\u0627\u0644\u0645\u0645\u0627\u0631\u0633\u0627\u062a \u0627\u0644\u0645\u062a\u062d\u0641\u064a\u0629 \u0641\u064a \u0627\u0644\u0645\u063a\u0631\u0628 \u0627\u0644\u0643\u0628\u064a\u0631."},
    },
    "intellectual-networks": {
        "en": {"title": "Intellectual Networks", "description": "Lineages, translation, and the circulation of knowledge across regions."},
        "fr": {"title": "R\u00e9seaux intellectuels", "description": "Lign\u00e9es, traductions et circulation des savoirs entre r\u00e9gions."},
        "es": {"title": "Redes intelectuales", "description": "L\u00edneas, traducciones y circulaci\u00f3n del conocimiento entre regiones."},
        "ar": {"title": "\u0627\u0644\u0634\u0628\u0643\u0627\u062a \u0627\u0644\u0641\u0643\u0631\u064a\u0629", "description": "\u0627\u0644\u0633\u0644\u0627\u0633\u0644 \u0627\u0644\u0639\u0644\u0645\u064a\u0629 \u0648\u0627\u0644\u062a\u0631\u062c\u0645\u0629 \u0648\u062a\u062f\u0627\u0648\u0644 \u0627\u0644\u0645\u0639\u0631\u0641\u0629 \u0628\u064a\u0646 \u0627\u0644\u0645\u0646\u0627\u0637\u0642."},
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

    # Seed curated translations for specific slugs
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
