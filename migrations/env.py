from logging.config import fileConfig
from typing import Any

from alembic import context

from app.db.session import Base, engine
from app.models import *  # noqa: F401,F403 - ensure models are imported for metadata

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url", str(engine.url))
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable: Any = config.attributes.get("connection")

    if connectable is None:
        connectable = engine.connect()
        close_connection = True
    else:
        close_connection = False

    try:
        context.configure(connection=connectable, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    finally:
        if close_connection:
            connectable.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
