from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.base import Base
import app.models  # noqa: F401 - registers models on Base.metadata

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)  # Activates Alembic logs on the terminal while running DB migrations

target_metadata = Base.metadata


def run_migrations_offline() -> None: # No database connection; Generates SQL scripts via terminal to a local .sql file; 
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, #Even without connecting, Alembic needs the URL prefix (postgresql+psycopg://...)
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction(): # Instead of sending queries over a network socket, Alembic simply prints the SQL statements (BEGIN;, ALTER TABLE ...;, UPDATE alembic_version ...;, COMMIT;) to the terminal.
        context.run_migrations()


def run_migrations_online() -> None: # Live Database Execution, Opens a live TCP connection to PostgreSQL.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction(): #Wraps the migration inside a Transactional DDL block
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline() #runs only when you pass the --sql flag
else:
    run_migrations_online()