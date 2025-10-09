# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Engine: low-level connection (PDO-like)
engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    pool_pre_ping=True
)

# Session factory: gives a new unit-of-work per request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
class Base(DeclarativeBase):
    pass
