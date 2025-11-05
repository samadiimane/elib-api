# scripts/seed_real_data.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import configure_mappers

from app.db.session import SessionLocal
from app.models import (
    Author,
    Category,
    CategoryKind,
    Journal,
    JournalIssue,
    Document,
    DocumentAuthor,
    DocumentType,
)

configure_mappers()


# -----------------------------
# Source data (from your sheet)
# -----------------------------

SECTIONS = [
    ("library", "Library", CategoryKind.section, None),
    ("journals", "Journals", CategoryKind.section, None),
    ("archives", "Archives & Documentary Heritage", CategoryKind.section, None),
    ("historical-sites", "Historical Sites & Landmarks", CategoryKind.section, None),
    ("research-themes", "Research Issues & Problematics", CategoryKind.section, None),
    ("publications", "Publications", CategoryKind.section, None),
]

SUBCATEGORIES = [
    # (slug, name, kind, description, parent_slug)
    ("manuscript", "Guide to Manuscript Collections", CategoryKind.archive_collection, None, "archives"),
]

JOURNALS = [
    # (slug, name, issn, publisher, description)
    ("dar-al-niaba", "Dar al-Niaba", None, "Khallouk Temsamani Abdelaziz", None),
    ("les-tangerois", "Les Tangérois", None, "Khallouk Temsamani Abdelaziz", None),
]

ISSUES = [
    # (journal_slug, year, volume, number, title, issue_date)
    ("dar-al-niaba", 1984, 1, 1, "فصلية وثائقية دراسية تعنى بتاريخ المغرب", date(1984, 1, 1)),
]

ARTICLES = [
    # Each article links by (journal_slug, issue_key = (year, volume, number))
    {
        "journal_slug": "dar-al-niaba",
        "issue_key": (1984, 1, 1),
        "title": "(19) الحياة الحضرية بطنجة في القرن",
        "abstract": (
            "تتصب جهود الباحثين المغاربة اليوم على التنقيب عن الوثائق والمخطوطات الوطنية لاعتمادها كنقطة أساسي "
            "لرسم صورة أمينة ومتكاملة عن التاريخ المغربي في مختلف عصوره وتخليصه من رواسب الفكر الاستعماري.\n\n"
            "وفي هذا الإطار يندرج مشروعنا المتواضع هو:\n"
            "أولاً: المساهمة في التعريف بالمستندات المغربية الحقبة من وثائق وكتابيش وتقاليد ونوازل.\n"
            "ثانياً: نشر أبحاث ودراسات تساهم في الكشف عن ماضينا وقيمنا وحضارتها.\n\n"
            "وأمنّا أن تكون هذه المجلة منبرا مفتوحا لكل الباحثين الراغبين في نشر المعرفة التاريخية "
            "المجردة عن الأهواء والأحكام الجاهزة."
        ),
        "lang": "ar",
        "year": 1984,
        "start_page": 1,
        "end_page": 79,
        # "primary_category_slug": None,  # add later if you create a suitable topic
    },
]


# -----------------------------
# Helpers (idempotent upserts)
# -----------------------------

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


def ensure_lead_author(session) -> Author:
    return get_or_create_author(session, *DAR_AL_NIABA_AUTHOR_PROFILE)


def get_category(session, slug: str) -> Optional[Category]:
    return session.execute(select(Category).where(Category.slug == slug)).scalar_one_or_none()

def ensure_category(session, *, slug: str, name: str, kind: CategoryKind,
                    description: Optional[str], parent: Optional[Category]) -> Category:
    c = get_category(session, slug)
    if c:
        c.name = name
        c.kind = kind
        c.description = description
        if parent and c.parent_id != parent.id:
            c.parent = parent
        return c
    c = Category(slug=slug, name=name, kind=kind, description=description, parent=parent)
    session.add(c)
    session.flush()
    return c

def ensure_journal(session, *, slug: str, name: str, issn: Optional[str],
                   publisher: Optional[str], description: Optional[str]) -> Journal:
    j = session.execute(select(Journal).where(Journal.slug == slug)).scalar_one_or_none()
    if j:
        j.name = name
        j.issn = issn
        j.publisher = publisher
        j.description = description
        return j
    j = Journal(slug=slug, name=name, issn=issn, publisher=publisher, description=description)
    session.add(j)
    session.flush()
    return j

def ensure_issue(session, *, journal: Journal, year: Optional[int],
                 volume: Optional[int], number: Optional[int],
                 title: Optional[str], issue_date: Optional[date]) -> JournalIssue:
    q = (
        select(JournalIssue)
        .where(JournalIssue.journal_id == journal.id)
        .where(JournalIssue.year == year)
        .where(JournalIssue.volume == volume)
        .where(JournalIssue.number == number)
    )
    issue = session.execute(q).scalar_one_or_none()
    if issue:
        issue.title = title
        issue.issue_date = issue_date
        return issue
    issue = JournalIssue(
        journal=journal, year=year, volume=volume, number=number, title=title, issue_date=issue_date
    )
    session.add(issue)
    session.flush()
    return issue

def ensure_article(session, *, journal: Journal, issue: JournalIssue, payload: dict) -> Document:
    d = (
        session.execute(
            select(Document)
            .where(Document.title == payload["title"])
            .order_by(Document.id.asc())
        )
        .scalars()
        .first()
    )
    pages = None
    if payload.get("start_page") is not None and payload.get("end_page") is not None:
        pages = max(payload["end_page"] - payload["start_page"] + 1, 1)

    primary_cat = None
    pcs = payload.get("primary_category_slug")
    if pcs:
        primary_cat = get_category(session, pcs)

    if d:
        d.abstract = payload.get("abstract")
        d.type = DocumentType.article
        d.lang = payload.get("lang") or "und"
        d.year = payload.get("year")
        d.start_page = payload.get("start_page")
        d.end_page = payload.get("end_page")
        d.pages = pages
        d.journal = journal
        d.issue = issue
        d.primary_category = primary_cat
    else:
        d = Document(
            title=payload["title"],
            abstract=payload.get("abstract"),
            type=DocumentType.article,
            lang=payload.get("lang") or "und",
            year=payload.get("year"),
            start_page=payload.get("start_page"),
            end_page=payload.get("end_page"),
            pages=pages,
            journal=journal,
            issue=issue,
            primary_category=primary_cat,
        )
        session.add(d)
        session.flush()

    lead_author = ensure_lead_author(session)
    set_document_authors(d, [lead_author])
    return d


# -----------------------------
# Main seeding routine
# -----------------------------

def run() -> None:
    s = SessionLocal()
    try:
        # 1) Sections
        parents = {}
        for slug, name, kind, desc in SECTIONS:
            parents[slug] = ensure_category(s, slug=slug, name=name, kind=kind, description=desc, parent=None)

        # 2) Subcategories
        for slug, name, kind, desc, parent_slug in SUBCATEGORIES:
            parent = parents[parent_slug]
            ensure_category(s, slug=slug, name=name, kind=kind, description=desc, parent=parent)

        # 3) Journals (+ journal categories under /journals)
        journals_parent = parents["journals"]
        journal_by_slug: dict[str, Journal] = {}
        for slug, name, issn, publisher, description in JOURNALS:
            j = ensure_journal(s, slug=slug, name=name, issn=issn, publisher=publisher, description=description)
            # make/attach the navigation node (kind=journal) under /journals and link it to the journal
            jc = ensure_category(s, slug=slug, name=name, kind=CategoryKind.journal, description=None, parent=journals_parent)
            jc.journal = j
            journal_by_slug[slug] = j

        # 4) Issues
        issue_index: dict[tuple[str, int, int, int], JournalIssue] = {}
        for jslug, year, volume, number, title, dte in ISSUES:
            j = journal_by_slug[jslug]
            issue = ensure_issue(s, journal=j, year=year, volume=volume, number=number, title=title, issue_date=dte)
            issue_index[(jslug, year, volume, number)] = issue

        # 5) Articles
        for a in ARTICLES:
            j = journal_by_slug[a["journal_slug"]]
            y, v, n = a["issue_key"]
            issue = issue_index[(a["journal_slug"], y, v, n)]
            ensure_article(s, journal=j, issue=issue, payload=a)

        s.commit()
        print("Seeded sections, subcategories, journals, one issue, and one article.")
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


if __name__ == "__main__":
    run()
