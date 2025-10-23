# app/repositories/journals.py
from __future__ import annotations
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
from app.models.journal import Journal, JournalIssue
from app.models.document import Document

def list_journals(
    db: Session,
    q: str | None,
    sort: str,           # "name asc" | "name desc"
    page: int,
    page_size: int,
):
    stmt = select(Journal)
    if q:
        ilike = f"%{q.strip()}%"
        stmt = stmt.where(Journal.name.ilike(ilike))

    if sort == "name asc":
        stmt = stmt.order_by(Journal.name.asc())
    else:
        stmt = stmt.order_by(Journal.name.desc())

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.execute(
        stmt.limit(page_size).offset((page - 1) * page_size)
    ).scalars().all()

    return items, total

def get_journal_by_slug(db: Session, slug: str) -> Journal | None:
    stmt = (
        select(Journal)
        .options(selectinload(Journal.issues))
        .where(Journal.slug == slug)
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
):
    stmt = select(JournalIssue).where(JournalIssue.journal_id == journal_id)

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

    return items, total

def list_documents_for_journal(db: Session, journal_id: int, page: int, page_size: int):
    stmt = (
        select(Document)
        .where(Document.journal_id == journal_id)
        .options(selectinload(Document.primary_category))
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
        .options(selectinload(Document.primary_category))
        .order_by(Document.start_page.asc().nulls_last(), Document.title.asc())
    )
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.execute(
        stmt.limit(page_size).offset((page - 1) * page_size)
    ).scalars().all()
    return items, total
