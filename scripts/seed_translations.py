"""
One-off seeder to populate curated journal translations for fr/es/ar.

Usage (from repo root):
    python scripts/seed_translations.py            # seeds fr, es, ar defaults
    python scripts/seed_translations.py --locales fr es  # seed a subset

Behavior:
- Upserts (journal_id, locale) with provided titles/descriptions/publishers.
- Safe to re-run; uses ON CONFLICT DO UPDATE.
- Works with configured DATABASE_URL; ensure SQLite database is not locked.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

import sqlalchemy as sa
from sqlalchemy.orm import Session

# Ensure project root is on sys.path when run directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.session import engine


TRANSLATIONS = [
    # journal_id = 1 — Dar al-Niaba
    {"journal_id": 1, "locale": "fr", "title": "Dar al-Niaba", "description": "Revue consacrée aux archives et à l’histoire du nord du Maroc.", "publisher": "Khallouk Temsamani Abdelaziz"},
    {"journal_id": 1, "locale": "es", "title": "Dar al-Niaba", "description": "Revista dedicada a los archivos y a la historia del norte de Marruecos.", "publisher": "Khallouk Temsamani Abdelaziz"},
    {"journal_id": 1, "locale": "ar", "title": "دار النيابة", "description": "دورية تُعنى بالأرشيفات وتاريخ شمال المغرب.", "publisher": "عبد العزيز خلوق التمسماني"},

    # journal_id = 2 — Les Tangérois
    {"journal_id": 2, "locale": "fr", "title": "Les Tangérois", "description": "Revue dédiée à la mémoire et à la société de Tanger, à ses réseaux intellectuels et à sa vie culturelle.", "publisher": "Khallouk Temsamani Abdelaziz"},
    {"journal_id": 2, "locale": "es", "title": "Los Tangerinos", "description": "Revista dedicada a la memoria y a la sociedad de Tánger, sus redes intelectuales y su vida cultural.", "publisher": "Khallouk Temsamani Abdelaziz"},
    {"journal_id": 2, "locale": "ar", "title": "الطنجاويون", "description": "مجلة تُعنى بذاكرة طنجة ومجتمعها وشبكاتها الفكرية وحياتها الثقافية.", "publisher": "عبد العزيز خلوق التمسماني"},

    # journal_id = 3 — Maghribi Studies Review
    {"journal_id": 3, "locale": "fr", "title": "Revue d’études maghrébines", "description": "Revue interdisciplinaire consacrée à l’histoire, à la culture et aux sociétés du Maghreb et de la Méditerranée occidentale.", "publisher": "Centre d’études historiques du Maghreb"},
    {"journal_id": 3, "locale": "es", "title": "Revista de Estudios Magrebíes", "description": "Revista interdisciplinaria sobre la historia, la cultura y las sociedades del Magreb y del Mediterráneo occidental.", "publisher": "Centro de Estudios Históricos del Magreb"},
    {"journal_id": 3, "locale": "ar", "title": "مجلة الدراسات المغاربية", "description": "مجلة متعددة التخصصات تُعنى بتاريخ وثقافة ومجتمعات المغرب العربي والبحر الأبيض المتوسط الغربي.", "publisher": "مركز الدراسات التاريخية للمغرب العربي"},

    # journal_id = 4 — Revue d’Histoire Méditerranéenne
    {"journal_id": 4, "locale": "fr", "title": "Revue d’Histoire Méditerranéenne", "description": "Revue trimestrielle de langue française consacrée aux histoires des mondes méditerranéens, de l’Antiquité à l’époque contemporaine.", "publisher": "Institut des Études Méditerranéennes"},
    {"journal_id": 4, "locale": "es", "title": "Revista de Historia Mediterránea", "description": "Revista trimestral en francés dedicada a las historias de los mundos mediterráneos, desde la Antigüedad hasta la época contemporánea.", "publisher": "Instituto de Estudios Mediterráneos"},
    {"journal_id": 4, "locale": "ar", "title": "مجلة التاريخ المتوسطي", "description": "مجلة فصلية باللغة الفرنسية مكرّسة لتاريخ العوالم المتوسطية من العصور القديمة إلى العصر الحديث.", "publisher": "معهد الدراسات المتوسطية"},

    # journal_id = 5 — Majallat al-Athar
    {"journal_id": 5, "locale": "fr", "title": "Revue des Antiquités", "description": "Revue de langue arabe consacrée à l’archéologie, à la conservation du patrimoine et à la culture matérielle en Afrique du Nord et en Méditerranée.", "publisher": "Centre de Recherches Patrimoniales"},
    {"journal_id": 5, "locale": "es", "title": "Revista de Antigüedades", "description": "Revista en árabe dedicada a la arqueología, la conservación del patrimonio y la cultura material en el norte de África y el Mediterráneo.", "publisher": "Centro de Investigaciones Patrimoniales"},
    {"journal_id": 5, "locale": "ar", "title": "مجلة الآثار", "description": "مجلة باللغة العربية متخصصة في علم الآثار وصون التراث والثقافة المادية في شمال أفريقيا وحوض المتوسط.", "publisher": "مركز البحوث التراثية"},

    # journal_id = 6 — imanu2 (test)
    {"journal_id": 6, "locale": "fr", "title": "imanu2", "description": "Salut, je suis Imane.", "publisher": "Samadi Press12"},
    {"journal_id": 6, "locale": "es", "title": "imanu2", "description": "Hola, soy Imane.", "publisher": "Samadi Press12"},
    {"journal_id": 6, "locale": "ar", "title": "إيمانو٢", "description": "مرحباً، أنا إيمان.", "publisher": "سامدي برس 12"},

    # journal_id = 7 — jedidaton (test)
    {"journal_id": 7, "locale": "fr", "title": "jedidaton", "description": "Salut.", "publisher": "JedidaPress12"},
    {"journal_id": 7, "locale": "es", "title": "jedidaton", "description": "Hola.", "publisher": "JedidaPress12"},
    {"journal_id": 7, "locale": "ar", "title": "جديداتون", "description": "مرحباً.", "publisher": "جديدة برس 12"},
]


def seed_translations(locales: Iterable[str]) -> None:
    normalized_locales = { (loc or "").strip().lower() for loc in locales if (loc or "").strip() }
    if not normalized_locales:
        print("No locales provided; nothing to do.")
        return

    rows = [row for row in TRANSLATIONS if row["locale"] in normalized_locales]
    if not rows:
        print("No matching translations for requested locales.")
        return

    print(f"Seeding/upserting {len(rows)} translation rows for locales: {', '.join(sorted(normalized_locales))}")

    upsert_stmt = sa.text(
        """
        INSERT INTO journal_translations (journal_id, locale, title, description, publisher)
        VALUES (:journal_id, :locale, :title, :description, :publisher)
        ON CONFLICT (journal_id, locale) DO UPDATE
        SET title = excluded.title,
            description = excluded.description,
            publisher = excluded.publisher
        """
    )

    with Session(engine, future=True) as db:
        for row in rows:
            db.execute(upsert_stmt, row)
        db.commit()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Seed curated journal translations (fr/es/ar).")
    parser.add_argument("--locales", nargs="+", required=False, default=["fr", "es", "ar"], help="Locales to seed.")
    args = parser.parse_args(argv)

    try:
        seed_translations(args.locales)
    except Exception as exc:  # noqa: BLE001
        print(f"Error while seeding translations: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
