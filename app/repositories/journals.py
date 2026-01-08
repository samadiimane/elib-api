# app/repositories/journals.py
from __future__ import annotations
from sqlalchemy import select, func, or_, case
from sqlalchemy.orm import Session, selectinload, aliased
from app.models.journal import Journal, JournalIssue, JournalTranslation
from app.models.document import Document
from app.models.author import Author
from app.core.config import settings

def list_journals(
    db: Session,
    q: str | None,
    sort: str,           # "name asc" | "name desc"
    page: int,
    page_size: int,
    locale: str | None = None,
):
    normalized_locale = _normalize_locale(locale)
    translation_subq = _best_translation_subquery(normalized_locale)

    stmt = (
        select(Journal)
        .options(selectinload(Journal.translations))
        .where(Journal.deleted_at.is_(None))
    )
    if translation_subq is not None:
        stmt = stmt.join(
            translation_subq,
            (translation_subq.c.journal_id == Journal.id)
            & (or_(translation_subq.c.rn == 1, translation_subq.c.rn.is_(None))),
            isouter=True,
        )

    localized_title = translation_subq.c.title if translation_subq is not None else Journal.name
    if q:
        ilike = f"%{q.strip()}%"
        conditions = [Journal.name.ilike(ilike), Journal.description.ilike(ilike)]
        if translation_subq is not None:
            conditions.insert(0, localized_title.ilike(ilike))
        stmt = stmt.where(or_(*conditions))

    if sort == "name asc":
        stmt = stmt.order_by(localized_title.asc())
    else:
        stmt = stmt.order_by(localized_title.desc())

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.execute(
        stmt.limit(page_size).offset((page - 1) * page_size)
    ).scalars().all()

    dto_items = [journal_to_dto(j, normalized_locale) for j in items]
    return dto_items, total

def get_journal_by_slug(db: Session, slug: str, locale: str | None = None) -> Journal | None:
    stmt = (
        select(Journal)
        .options(
            selectinload(Journal.issues),
            selectinload(Journal.translations),
        )
        .where(Journal.slug == slug)
        .where(Journal.deleted_at.is_(None))
    )
    return db.execute(stmt).scalar_one_or_none()

def journal_counts(db: Session, journal_id: int):
    issues_count = db.scalar(
        select(func.count()).select_from(JournalIssue).where(JournalIssue.journal_id == journal_id)
    ) or 0
    docs_count = db.scalar(
        select(func.count()).select_from(Document).where(Document.journal_id == journal_id)
    ) or 0
    return {"issues": issues_count, "documents": docs_count}

def list_issues(
    db: Session,
    journal_id: int,
    year: int | None,
    volume: int | None,
    number: int | None,
    sort: str,           # "year desc" | "year asc" | "vol asc" | "vol desc" | "num asc" | "num desc"
    page: int,
    page_size: int,
    locale: str | None = None,
):
    stmt = (
        select(JournalIssue)
        .where(JournalIssue.journal_id == journal_id)
    )

    if year is not None:
        stmt = stmt.where(JournalIssue.year == year)
    if volume is not None:
        stmt = stmt.where(JournalIssue.volume == volume)
    if number is not None:
        stmt = stmt.where(JournalIssue.number == number)

    order = {
        "year desc": JournalIssue.year.desc(),
        "year asc":  JournalIssue.year.asc(),
        "vol asc":   JournalIssue.volume.asc().nulls_last(),
        "vol desc":  JournalIssue.volume.desc().nulls_last(),
        "num asc":   JournalIssue.number.asc().nulls_last(),
        "num desc":  JournalIssue.number.desc().nulls_last(),
    }.get(sort, JournalIssue.year.desc())
    stmt = stmt.order_by(order)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.execute(
        stmt.limit(page_size).offset((page - 1) * page_size)
    ).scalars().all()

    normalized_locale = _normalize_locale(locale)
    dto_items = [issue_to_dto(i, normalized_locale) for i in items]
    return dto_items, total

def list_documents_for_journal(db: Session, journal_id: int, page: int, page_size: int):
    stmt = (
        select(Document)
        .where(Document.journal_id == journal_id)
        .options(
            selectinload(Document.primary_category),
            selectinload(Document.authors).load_only(
                Author.id,
                Author.full_name_ar,
                Author.full_name_lat,
                Author.affiliation,
            ),
        )
        .order_by(Document.created_at.desc())
    )
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.execute(
        stmt.limit(page_size).offset((page - 1) * page_size)
    ).scalars().all()
    return items, total

def list_documents_for_issue(db: Session, issue_id: int, page: int, page_size: int):
    stmt = (
        select(Document)
        .where(Document.issue_id == issue_id)
        .options(
            selectinload(Document.primary_category),
            selectinload(Document.authors).load_only(
                Author.id,
                Author.full_name_ar,
                Author.full_name_lat,
                Author.affiliation,
            ),
        )
        .order_by(Document.start_page.asc().nulls_last(), Document.title.asc())
    )
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.execute(
        stmt.limit(page_size).offset((page - 1) * page_size)
    ).scalars().all()
    return items, total


def _normalize_locale(locale: str | None) -> str:
    return (locale or settings.default_locale or "en").strip().lower()


def _candidate_locales(locale: str) -> list[str]:
    requested = locale.strip().lower()
    default_locale = (settings.default_locale or "en").strip().lower()
    candidates: list[str] = []
    if requested:
        candidates.append(requested)
        if "-" in requested:
            base = requested.split("-")[0]
            if base:
                candidates.append(base)
    candidates.append(default_locale)

    dedup: list[str] = []
    seen: set[str] = set()
    for cand in candidates:
        if cand and cand not in seen:
            dedup.append(cand)
            seen.add(cand)
    return dedup


def _pick_translation(translations, locale: str):
    for cand in _candidate_locales(locale):
        for t in translations or []:
            if t.locale == cand:
                return t
    return None


def _best_translation_subquery(locale: str):
    candidates = _candidate_locales(locale)
    if not candidates:
        return None

    jt = aliased(JournalTranslation)
    priority_case = case(
        *((jt.locale == cand, idx) for idx, cand in enumerate(candidates)),
        else_=len(candidates) + 1,
    )

    subq = (
        select(
            jt.journal_id.label("journal_id"),
            jt.title.label("title"),
            jt.description.label("description"),
            jt.publisher.label("publisher"),
            func.row_number()
            .over(partition_by=jt.journal_id, order_by=priority_case)
            .label("rn"),
        )
        .where(jt.locale.in_(candidates))
        .subquery()
    )
    return subq


def journal_to_dto(journal: Journal, locale: str) -> dict:
    translation = _pick_translation(journal.translations, locale)
    return {
        "id": journal.id,
        "slug": journal.slug,
        "name": translation.title if translation and translation.title is not None else journal.name,
        "issn": journal.issn,
        "publisher": (
            translation.publisher
            if translation and translation.publisher is not None
            else journal.publisher
        ),
        "description": (
            translation.description
            if translation and translation.description is not None
            else journal.description
        ),
    }


def issue_to_dto(issue: JournalIssue, locale: str) -> dict:
    return {
        "id": issue.id,
        "volume": issue.volume,
        "number": issue.number,
        "year": issue.year,
        "title": issue.title,
        "description": None,
        "issue_date": issue.issue_date,
    }
