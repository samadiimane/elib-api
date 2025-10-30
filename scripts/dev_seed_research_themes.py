"""Seed research theme documents for demo data.

Run order:
1) python -m scripts.dev_seed_categories
2) python -m scripts.dev_seed_journals
3) python -m scripts.dev_seed_archives
4) python -m scripts.dev_seed_sites
5) python -m scripts.dev_seed_research_themes
6) python -m scripts.dev_seed_publications

Quick verification:
curl "http://127.0.0.1:8010/v1/categories?parent=research-themes"
curl "http://127.0.0.1:8010/v1/search/documents?category_slug=material-culture"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from sqlalchemy import select
from sqlalchemy.orm import configure_mappers

from app.db.session import SessionLocal
from app.models import Category, CategoryKind, Document, DocumentType

configure_mappers()


@dataclass(frozen=True)
class DocumentSeed:
    title: str
    abstract: str
    lang: str
    year: int
    doc_type: DocumentType
    primary_category_slug: str
    pages: int | None = None
    doi: str | None = None
    isbn: str | None = None
    issn: str | None = None


CATEGORY_DEFAULTS = {
    "research-themes": (
        "Research Themes",
        CategoryKind.section,
        "Cross-cutting scholarly conversations that link archives, fieldwork, and interpretive communities.",
        None,
    ),
    "urban-histories": (
        "Urban Histories",
        CategoryKind.topic,
        "Neighbourhoods, governance, and the rhythms of everyday urban life.",
        "research-themes",
    ),
    "material-culture": (
        "Material Culture",
        CategoryKind.topic,
        "Objects, artisanship, and museum practices across the Maghrib.",
        "research-themes",
    ),
    "intellectual-networks": (
        "Intellectual Networks",
        CategoryKind.topic,
        "Lineages, translation, and the circulation of knowledge across languages and regions.",
        "research-themes",
    ),
}


THEME_SEEDS: tuple[DocumentSeed, ...] = (
    DocumentSeed(
        title="Mapping Municipal Tramways in Casablanca, 1910-1955",
        abstract=(
            "This article reconstructs the municipal tramway concessions that shaped Casablanca's growth. "
            "It combines protectorate engineering files with oral histories from conductors. "
            "Interactive maps illustrate the shifting boundaries of mixed neighbourhoods along each line."
        ),
        lang="en",
        year=2020,
        doc_type=DocumentType.article,
        primary_category_slug="urban-histories",
        pages=34,
        doi="10.48231/atlas.2020.tramways",
    ),
    DocumentSeed(
        title="دفتر يوميات حارس المدينة القديمة بفاس",
        abstract=(
            "يتضمن هذا الدفتر اليومي ملاحظات حارس السور الشرقي لفاس خلال سنوات 1941-1943. "
            "يصف في صفحات موجزة تحركات السكان، وتوزيع الخبز، وردود فعل السكان تجاه المراقبة الليلية. "
            "تقدم الهوامش مصطلحات دارجة ومحلية تساعد على قراءة التحولات الحضرية."
        ),
        lang="ar",
        year=1944,
        doc_type=DocumentType.manuscript,
        primary_category_slug="urban-histories",
    ),
    DocumentSeed(
        title="Enquête sur les coopératives d'habitat à Rabat",
        abstract=(
            "Ce rapport analyse les coopératives d'habitat qui ont structuré les périphéries de Rabat dans les années 1970. "
            "Les archives municipales sont croisées avec des entretiens menés auprès des fondatrices. "
            "Des annexes cartographiques retracent les étapes d'équipement des quartiers autoconstruits."
        ),
        lang="fr",
        year=1978,
        doc_type=DocumentType.report,
        primary_category_slug="urban-histories",
        pages=119,
    ),
    DocumentSeed(
        title="Catalogue raisonné des ateliers de cuivre à Marrakech",
        abstract=(
            "Ce catalogue documente vingt ateliers de cuivre actifs dans le souk Haddadine à Marrakech. "
            "Il décrit les lignages familiaux، يورد أسماء المعلمين والتلاميذ، ويحلل تقنيات الزخرفة. "
            "Une série de diagrammes illustre les chaînes d'approvisionnement en métaux et en charbon."
        ),
        lang="fr",
        year=1982,
        doc_type=DocumentType.report,
        primary_category_slug="material-culture",
        pages=87,
    ),
    DocumentSeed(
        title="Threading Memory: Amazigh Textile Exchanges",
        abstract=(
            "The essay examines the exchange circuits connecting Amazigh weavers in the Rif and the Middle Atlas. "
            "It analyses colour palettes and motif transmission using digitised sample books. "
            "Field interviews from the 2010s are juxtaposed with 1930s ethnographic films to show continuity."
        ),
        lang="en",
        year=2018,
        doc_type=DocumentType.article,
        primary_category_slug="material-culture",
        pages=41,
        doi="10.48231/atlas.2018.textiles",
    ),
    DocumentSeed(
        title="دفتر صناع الطرز الفاسي",
        abstract=(
            "يجمع هذا الدفتر أنماطاً دقيقة من الطرز الفاسي تم تدوينها في ثلاثينيات القرن العشرين. "
            "يشرح قواعد الألوان، ويحدد الأقمشة المستخدمة، ويورد أسماء المعلمات في مدارس الصناع. "
            "ترافق النص رسومات مرسومة بالحبر وملحوظات حول تكييف الزخارف في المناسبات الدينية."
        ),
        lang="ar",
        year=1935,
        doc_type=DocumentType.manuscript,
        primary_category_slug="material-culture",
    ),
    DocumentSeed(
        title="Networks of Translation between Tetouan and Cádiz, 1780-1850",
        abstract=(
            "This article traces translators who bridged Arabic and Spanish legal vocabularies during the late eighteenth century. "
            "Shipping manifests and diplomatic notebooks reveal itineraries that tied Tetouan notaries to Cádiz merchants. "
            "Marginalia from bilingual treaties show how jurists negotiated concepts of neutrality."
        ),
        lang="en",
        year=2015,
        doc_type=DocumentType.article,
        primary_category_slug="intellectual-networks",
        pages=52,
        doi="10.48231/atlas.2015.translation",
    ),
    DocumentSeed(
        title="رسائل العلماء بين فاس وتونس (1901-1910)",
        abstract=(
            "تحوي هذه المجموعة رسائل علمية متبادلة بين أساتذة جامعة القرويين وزملائهم بجامع الزيتونة. "
            "تناقش الرسائل منهجية تدريس الفقه المقارن، وترصد انتقال الطلبة بين المدينتين. "
            "تشير التعليقات الهامشية إلى تبادل نسخ الكتب وطرق توزيع الزوايا لرسائل التزكية."
        ),
        lang="ar",
        year=1911,
        doc_type=DocumentType.manuscript,
        primary_category_slug="intellectual-networks",
    ),
    DocumentSeed(
        title="Thesis: Pedagogies of the Qarawiyyin Reform, 1947-1964",
        abstract=(
            "This doctoral thesis analyses the pedagogical reforms introduced at the Qarawiyyin across two decades. "
            "Archival minutes from reform councils are paired with alumni memoirs and lesson notebooks. "
            "The conclusion compares shifts in curriculum design to parallel experiments in Tunis and Cairo."
        ),
        lang="en",
        year=2022,
        doc_type=DocumentType.thesis,
        primary_category_slug="intellectual-networks",
        pages=326,
        isbn="978-1-58474-092-3",
    ),
)


def get_category_by_slug(session, slug: str) -> Category | None:
    return session.execute(select(Category).where(Category.slug == slug)).scalar_one_or_none()


def ensure_category(
    session,
    *,
    slug: str,
    name: str,
    kind: CategoryKind,
    description: str,
    parent: Category | None = None,
) -> tuple[Category, bool, bool]:
    category = get_category_by_slug(session, slug)
    if category is None:
        category = Category(
            slug=slug,
            name=name,
            kind=kind,
            description=description,
            parent=parent,
        )
        session.add(category)
        session.flush()
        return category, True, False

    updated = False
    if category.name != name:
        category.name = name
        updated = True
    if category.kind != kind:
        category.kind = kind
        updated = True
    if category.description != description:
        category.description = description
        updated = True
    if parent is None and category.parent_id is not None:
        category.parent = None
        updated = True
    if parent is not None and category.parent_id != parent.id:
        category.parent = parent
        updated = True
    return category, False, updated


def ensure_required_categories(session) -> dict[str, Category]:
    resolved: dict[str, Category] = {}
    for slug, (name, kind, description, parent_slug) in CATEGORY_DEFAULTS.items():
        parent = resolved.get(parent_slug) if parent_slug else None
        if parent_slug and parent is None:
            parent = get_category_by_slug(session, parent_slug)
            if parent is None:
                parent_name, parent_kind, parent_desc, _ = CATEGORY_DEFAULTS[parent_slug]
                parent, _, _ = ensure_category(
                    session,
                    slug=parent_slug,
                    name=parent_name,
                    kind=parent_kind,
                    description=parent_desc,
                    parent=None,
                )
            resolved[parent_slug] = parent
        category, _, _ = ensure_category(
            session,
            slug=slug,
            name=name,
            kind=kind,
            description=description,
            parent=parent,
        )
        resolved[slug] = category
    return resolved


def upsert_document(session, seed: DocumentSeed, categories: dict[str, Category]) -> tuple[bool, bool]:
    document = session.execute(select(Document).where(Document.title == seed.title)).scalar_one_or_none()
    created = False
    updated = False
    category = categories[seed.primary_category_slug]

    def maybe_set(obj: Document, attr: str, value):
        nonlocal updated
        if getattr(obj, attr) != value:
            setattr(obj, attr, value)
            updated = True

    if document is None:
        document = Document(
            title=seed.title,
            abstract=seed.abstract,
            lang=seed.lang,
            year=seed.year,
            type=seed.doc_type,
            pages=seed.pages,
            doi=seed.doi,
            isbn=seed.isbn,
            issn=seed.issn,
            primary_category=category,
        )
        session.add(document)
        session.flush()
        created = True
        return created, updated

    maybe_set(document, "abstract", seed.abstract)
    maybe_set(document, "lang", seed.lang)
    maybe_set(document, "year", seed.year)
    if document.type != seed.doc_type:
        document.type = seed.doc_type
        updated = True
    maybe_set(document, "pages", seed.pages)
    maybe_set(document, "doi", seed.doi)
    maybe_set(document, "isbn", seed.isbn)
    maybe_set(document, "issn", seed.issn)
    if document.primary_category_id != category.id:
        document.primary_category = category
        updated = True
    return created, updated


def seed() -> None:
    session = SessionLocal()
    overall_inserted = 0
    overall_updated = 0
    per_topic: Dict[str, Dict[str, int]] = {
        "urban-histories": {"processed": 0, "inserted": 0, "updated": 0},
        "material-culture": {"processed": 0, "inserted": 0, "updated": 0},
        "intellectual-networks": {"processed": 0, "inserted": 0, "updated": 0},
    }
    try:
        categories = ensure_required_categories(session)
        for seed_row in THEME_SEEDS:
            created, changed = upsert_document(session, seed_row, categories)
            overall_inserted += int(created)
            overall_updated += int(changed and not created)
            topic_stats = per_topic[seed_row.primary_category_slug]
            topic_stats["processed"] += 1
            topic_stats["inserted"] += int(created)
            topic_stats["updated"] += int(changed and not created)

        session.commit()
        print(
            f"Research theme documents seeded — inserted: {overall_inserted}, updated: {overall_updated}, total: {len(THEME_SEEDS)}."
        )
        for slug, stats in per_topic.items():
            print(
                f"  - {slug}: processed={stats['processed']}, inserted={stats['inserted']}, updated={stats['updated']}"
            )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
