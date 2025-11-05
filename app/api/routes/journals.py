# app/api/routes/journals.py
from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.pagination import PaginatedResponse
from app.schemas.journal import JournalOut, JournalCounts, JournalDetailOut, JournalIssueOut
from app.schemas.document import DocumentOut
from app.repositories import journals as repo

router = APIRouter(prefix="/v1/journals", tags=["journals"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=PaginatedResponse[JournalOut])
def list_journals(
    q: str | None = Query(None),
    sort: str = Query("name asc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if sort not in {"name asc", "name desc"}:
        raise HTTPException(status_code=422, detail="Invalid sort")
    items, total = repo.list_journals(db, q, sort, page, page_size)
    payload = [JournalOut.model_validate(i.__dict__) for i in items]
    return PaginatedResponse[JournalOut](items=payload, total=total, page=page, page_size=page_size, has_next=(page*page_size < (total or 0)))

@router.get("/{slug}", response_model=JournalDetailOut)
def get_journal(slug: str = Path(...), db: Session = Depends(get_db)):
    j = repo.get_journal_by_slug(db, slug)
    if not j:
        raise HTTPException(status_code=404, detail="Journal not found")
    counts = repo.journal_counts(db, j.id)
    return JournalDetailOut(
        journal=JournalOut.model_validate(j.__dict__),
        counts=JournalCounts(**counts),
    )

@router.get("/{slug}/issues", response_model=PaginatedResponse[JournalIssueOut])
def list_journal_issues(
    slug: str,
    year: int | None = Query(None),
    volume: int | None = Query(None),
    number: int | None = Query(None),
    sort: str = Query("year desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if sort not in {"year desc","year asc","vol asc","vol desc","num asc","num desc"}:
        raise HTTPException(status_code=422, detail="Invalid sort")
    j = repo.get_journal_by_slug(db, slug)
    if not j:
        raise HTTPException(status_code=404, detail="Journal not found")
    items, total = repo.list_issues(db, j.id, year, volume, number, sort, page, page_size)
    payload = [JournalIssueOut.model_validate(i.__dict__) for i in items]
    return PaginatedResponse[JournalIssueOut](items=payload, total=total, page=page, page_size=page_size, has_next=(page*page_size < (total or 0)))

@router.get("/{slug}/articles", response_model=PaginatedResponse[DocumentOut])
def list_journal_articles(
    slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    j = repo.get_journal_by_slug(db, slug)
    if not j:
        raise HTTPException(status_code=404, detail="Journal not found")
    docs, total = repo.list_documents_for_journal(db, j.id, page, page_size)
    payload = [DocumentOut.model_validate(d) for d in docs]
    return PaginatedResponse[DocumentOut](items=payload, total=total, page=page, page_size=page_size, has_next=(page*page_size < (total or 0)))

@router.get("/{slug}/issues/{issue_id}/articles", response_model=PaginatedResponse[DocumentOut])
def list_issue_articles(
    slug: str,
    issue_id: int = Path(..., ge=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    j = repo.get_journal_by_slug(db, slug)
    if not j:
        raise HTTPException(status_code=404, detail="Journal not found")
    # Optional: verify issue belongs to journal
    docs, total = repo.list_documents_for_issue(db, issue_id, page, page_size)
    payload = [DocumentOut.model_validate(d) for d in docs]
    return PaginatedResponse[DocumentOut](items=payload, total=total, page=page, page_size=page_size, has_next=(page*page_size < (total or 0)))
