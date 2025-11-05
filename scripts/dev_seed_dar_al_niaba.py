"""Seed additional Dar al-Niaba issues with Arabic articles.

Run order:
1) python -m scripts.dev_seed_categories
2) python -m scripts.dev_seed_journals
3) python -m scripts.dev_seed_dar_al_niaba

Quick verification:
- curl "http://127.0.0.1:8010/v1/journals/dar-al-niaba"
- curl "http://127.0.0.1:8010/v1/journals/dar-al-niaba/issues?page_size=10"
- curl "http://127.0.0.1:8010/v1/search/documents?category=dar-al-niaba&lang=ar"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import configure_mappers

from app.db.session import SessionLocal
from app.models import (
    Author,
    Category,
    CategoryKind,
    Document,
    DocumentAuthor,
    DocumentType,
    Journal,
    JournalIssue,
)

configure_mappers()


@dataclass(frozen=True)
class ArticleSeed:
    title: str
    abstract: str
    year: int
    start_page: int | None = None
    end_page: int | None = None

    @property
    def page_span(self) -> int | None:
        if self.start_page is None or self.end_page is None:
            return None
        return max(self.end_page - self.start_page + 1, 1)


@dataclass(frozen=True)
class IssueSeed:
    year: int
    volume: int | None
    number: int | None
    title: str | None = None
    articles: tuple[ArticleSeed, ...] = field(default_factory=tuple)


DAR_AL_NIABA_AUTHOR_PROFILE: tuple[str, str | None, str | None] = (
    "عبد العزيز خلوق التمسماني",
    "Abdelaziz Khallouk Temsamani",
    "مؤسسة تمسماني للبحث والدراسات",
)

_AUTHOR_CACHE: dict[tuple[str, str | None, str | None], Author] = {}


def get_or_create_author(
    session,
    full_name_ar: str,
    full_name_lat: str | None = None,
    affiliation: str | None = None,
) -> Author:
    key = (full_name_ar, full_name_lat, affiliation)
    cached = _AUTHOR_CACHE.get(key)
    if cached is not None:
        return cached

    stmt = select(Author).where(Author.full_name_ar == full_name_ar)
    if full_name_lat is not None:
        stmt = stmt.where(Author.full_name_lat == full_name_lat)
    author = session.execute(stmt).scalar_one_or_none()

    if author is None:
        author = Author(
            full_name_ar=full_name_ar,
            full_name_lat=full_name_lat,
            affiliation=affiliation,
        )
        session.add(author)
        session.flush()
    else:
        updated = False
        if full_name_lat is not None and author.full_name_lat != full_name_lat:
            author.full_name_lat = full_name_lat
            updated = True
        if affiliation is not None and author.affiliation != affiliation:
            author.affiliation = affiliation
            updated = True
        if updated:
            session.flush()

    _AUTHOR_CACHE[key] = author
    return author


def ensure_lead_author(session) -> Author:
    return get_or_create_author(session, *DAR_AL_NIABA_AUTHOR_PROFILE)


def set_document_authors(document: Document, authors: Sequence[Author]) -> None:
    existing = {link.author_id: link for link in getattr(document, "author_links", [])}
    desired_ids: set[int] = set()

    for position, author in enumerate(authors, start=1):
        desired_ids.add(author.id)
        link = existing.get(author.id)
        if link is None:
            link = DocumentAuthor(author_id=author.id, position=position)
            document.author_links.append(link)
        else:
            link.position = position

    for link in list(getattr(document, "author_links", [])):
        if link.author_id not in desired_ids:
            document.author_links.remove(link)


ISSUE_SEEDS: tuple[IssueSeed, ...] = (
    IssueSeed(
        year=1951,
        volume=7,
        number=3,
        title="ملفات النيابة ومجالس الحسبة",
        articles=(
            ArticleSeed(
                title="محاضر تفتيش الأسواق في طنجة",
                abstract=(
                    "يعرض هذا المقال محاضر النيابة المتعلقة بمراقبة الأسواق، ويحلل دور المحتسب في "
                    "تنظيم التجارة وضبط الأسعار خلال صيف 1951."
                ),
                year=1951,
                start_page=5,
                end_page=22,
            ),
            ArticleSeed(
                title="القضاء العرفي وتحولات الضبط الحضري",
                abstract=(
                    "يتناول العلاقة بين القضاء العرفي والنيابة في ضبط المجال الحضري، اعتماداً على "
                    "تقارير عربية محفوظة في دار النيابة."
                ),
                year=1951,
                start_page=23,
                end_page=41,
            ),
            ArticleSeed(
                title="سد الديون على التجار المحليين",
                abstract=(
                    "يدرس هذا المقال ملفات تسوية الديون المرفوعة إلى النيابة، ويبرز أدوات الضبط "
                    "الإداري التي فرضتها السلطات المحلية."
                ),
                year=1951,
                start_page=42,
                end_page=57,
            ),
        ),
    ),
    IssueSeed(
        year=1952,
        volume=8,
        number=1,
        title="التوثيق العربي في دار النيابة",
        articles=(
            ArticleSeed(
                title="دفاتر الموثقين وعدالة العقود",
                abstract=(
                    "يتتبع مسار دفاتر الموثقين المحفوظة في دار النيابة، ويبرز كيفية اعتمادها لإثبات "
                    "الملكية في القضاء المحلي."
                ),
                year=1952,
                start_page=3,
                end_page=27,
            ),
            ArticleSeed(
                title="المترجمون وبناء الأرشيف المزدوج",
                abstract=(
                    "يعرض المقال أدوار المترجمين في صياغة العقود الثنائية اللغة، ويحلل أثرهم في "
                    "تسهيل التواصل بين النيابة والبعثات الدبلوماسية."
                ),
                year=1952,
                start_page=28,
                end_page=46,
            ),
        ),
    ),
)


def ensure_journals_category(session) -> Category:
    stmt = select(Category).where(Category.slug == "journals")
    category = session.execute(stmt).scalar_one_or_none()
    if category:
        return category

    category = Category(
        slug="journals",
        name="Journals",
        kind=CategoryKind.section,
        description="Serial publications that disseminate peer-reviewed scholarship across Maghribi studies.",
    )
    session.add(category)
    session.flush()
    return category


def ensure_journal(session, parent: Category) -> Journal:
    stmt = select(Journal).where(Journal.slug == "dar-al-niaba")
    journal = session.execute(stmt).scalar_one_or_none()
    if journal is None:
        journal = Journal(
            slug="dar-al-niaba",
            name="Dar al-Niaba",
            issn=None,
            publisher=None,
            description="Journal documenting the administrative records of the Tangier International Zone.",
        )
        session.add(journal)
        session.flush()

    stmt = select(Category).where(Category.slug == "dar-al-niaba")
    category = session.execute(stmt).scalar_one_or_none()
    if category is None:
        category = Category(
            slug="dar-al-niaba",
            name="Dar al-Niaba",
            kind=CategoryKind.journal,
            description="Bulletins, circulars, and administrative dossiers issued by the Residency.",
            parent=parent,
            journal=journal,
        )
        session.add(category)
    else:
        category.journal = journal
    return journal


def upsert_issue(session, journal: Journal, seed: IssueSeed) -> JournalIssue:
    stmt = (
        select(JournalIssue)
        .where(JournalIssue.journal_id == journal.id)
        .where(JournalIssue.year == seed.year)
        .where(JournalIssue.volume == seed.volume)
        .where(JournalIssue.number == seed.number)
    )
    issue = session.execute(stmt).scalar_one_or_none()
    if issue:
        issue.title = seed.title
    else:
        issue = JournalIssue(
            journal=journal,
            year=seed.year,
            volume=seed.volume,
            number=seed.number,
            title=seed.title,
        )
        session.add(issue)
        session.flush()
    return issue


def upsert_article(session, journal: Journal, issue: JournalIssue, seed: ArticleSeed) -> None:
    stmt = select(Document).where(Document.title == seed.title)
    document = session.execute(stmt.order_by(Document.id.asc())).scalars().first()

    if document:
        document.abstract = seed.abstract
        document.lang = "ar"
        document.year = seed.year
        document.start_page = seed.start_page
        document.end_page = seed.end_page
        document.pages = seed.page_span
        document.issue = issue
        document.journal = journal
    else:
        document = Document(
            title=seed.title,
            abstract=seed.abstract,
            type=DocumentType.article,
            lang="ar",
            year=seed.year,
            pages=seed.page_span,
            start_page=seed.start_page,
            end_page=seed.end_page,
            journal=journal,
            issue=issue,
        )
        session.add(document)

    lead_author = ensure_lead_author(session)
    set_document_authors(document, [lead_author])


def seed() -> None:
    session = SessionLocal()
    try:
        journals_parent = ensure_journals_category(session)
        journal = ensure_journal(session, journals_parent)

        for issue_seed in ISSUE_SEEDS:
            issue = upsert_issue(session, journal, issue_seed)
            for article_seed in issue_seed.articles:
                upsert_article(session, journal, issue, article_seed)

        session.commit()
        print("Seeded Dar al-Niaba issues with Arabic articles.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
