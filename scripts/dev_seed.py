# app/scripts/dev_seed.py
from app.db.session import SessionLocal, engine, Base
from app.models.library import Collection, Document

if __name__ == "__main__":
    # Ensure tables exist (ok to call again on SQLite)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # add a collection
        col = Collection(name="General Library", description="Books and monographs")
        db.add(col)
        db.flush()  # get col.id

        # add a document
        doc = Document(
            title="Introduction to Research",
            authors="A. Author; B. Writer",
            lang="en",
            type="book",
            year=2019,
            pages=220,
            collection_id=col.id,
            abstract="Basics of research methods."
        )
        db.add(doc)

        db.commit()
        print("Seeded 1 collection + 1 document.")
    finally:
        db.close()
