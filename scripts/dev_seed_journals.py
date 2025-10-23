# scripts/dev_seed_journals.py
from app.db.session import SessionLocal
from app.models.journal import Journal, JournalIssue
from app.models.document import Document, DocumentType
from sqlalchemy import select

def get_or_create(db, model, **kw):
    obj = db.execute(select(model).filter_by(**kw)).scalar_one_or_none()
    if obj:
        return obj, False
    obj = model(**kw)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj, True

def run():
    db = SessionLocal()
    try:
        j, _ = get_or_create(db, Journal, slug="dar-al-niaba", name="Dar al-Niaba")
        i1, _ = get_or_create(db, JournalIssue, journal_id=j.id, year=1925, volume=1, number=1, title="Inaugural issue")
        i2, _ = get_or_create(db, JournalIssue, journal_id=j.id, year=1925, volume=1, number=2, title="Issue 2")

        # attach a couple of documents if your table is empty
        d = Document(
            title="Trade and Consular Relations in Tangier",
            abstract="Sample abstract...",
            type=DocumentType.article,
            lang="en",
            year=1925,
            journal_id=j.id,
            issue_id=i1.id,
            start_page=1,
            end_page=12,
        )
        db.add(d)
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    run()
