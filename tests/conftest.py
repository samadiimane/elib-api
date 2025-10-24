from __future__ import annotations

from pathlib import Path
from typing import Generator

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]

# Ensure the application package is importable without installing it.
import sys

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def run_upgrade(engine: Engine, config: Config, revision: str) -> None:
    """Run an Alembic upgrade within an explicit connection."""
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, revision)
    config.attributes.pop("connection", None)


@pytest.fixture()
def alembic_engine(tmp_path: Path) -> Generator[tuple[Engine, Config], None, None]:
    """Provide a dedicated SQLite engine and Alembic config per test."""
    config = Config(str(ROOT_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT_DIR / "migrations"))

    db_path = tmp_path / "test.db"
    url = f"sqlite:///{db_path}"
    config.set_main_option("sqlalchemy.url", url)

    engine = sa.create_engine(url, future=True)
    try:
        yield engine, config
    finally:
        engine.dispose()


@pytest.fixture()
def head_database(alembic_engine: tuple[Engine, Config]) -> Generator[tuple[sessionmaker, Engine], None, None]:
    """Upgrade the temporary database to the latest revision and return a session factory."""
    engine, config = alembic_engine
    run_upgrade(engine, config, "head")
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    try:
        yield SessionLocal, engine
    finally:
        SessionLocal.close_all()
