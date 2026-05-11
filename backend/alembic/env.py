from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

from app.core.config import settings
from app.core.database import Base

# Import all models so Alembic sees them for autogenerate
from app.models import Job, Asset, Property, User  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Convert async URL to sync for Alembic (psycopg2 locally, asyncpg in Docker)
def get_sync_url() -> str:
    url = settings.database_url
    # Strip async driver prefixes for Alembic sync connection
    return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://") \
              .replace("postgresql+psycopg://", "postgresql+psycopg2://")

config.set_main_option("sqlalchemy.url", get_sync_url())


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        get_sync_url(),
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
