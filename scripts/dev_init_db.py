# scripts/dev_init_db.py
from app.db.session import engine, Base
from app.models import *  # registers models

if __name__ == "__main__":
    print("Creating tables on SQLite dev.db ...")
    Base.metadata.create_all(bind=engine)
    print("Done.")
