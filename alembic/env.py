from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

from server.db.engine import engine
from sqlmodel import SQLModel

# импорт моделей ОБЯЗАТЕЛЕН
from server.db.models.user import User  # noqa
from server.db.models.session import UserSession  # noqa

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# КЛЮЧЕВАЯ СТРОКА
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=str(engine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
