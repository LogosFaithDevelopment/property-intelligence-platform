"""Alembic environment configuration"""

from logging.config import fileConfig

from alembic import context
from app.config import get_settings
from app.models.api_cache import APICache
from app.models.assessment import Assessment
# Import all models to ensure they're registered with SQLAlchemy
from app.models.base import BaseModel
from app.models.church import Church
from app.models.property import Property
from app.models.report import Report
from sqlalchemy import pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get database URL from settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = BaseModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    from sqlalchemy import engine_from_config

    # Convert async URL to sync URL for migrations
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}
    
    # Replace asyncpg/async driver with sync psycopg2
    db_url = configuration.get('sqlalchemy.url', '')
    if 'asyncpg' in db_url:
        db_url = db_url.replace('postgresql+asyncpg', 'postgresql+psycopg2')
    elif 'postgresql://' in db_url and '+' not in db_url:
        db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://')
    
    configuration['sqlalchemy.url'] = db_url
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
