from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.models.base import Base

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _add_column_if_missing(table: str, column: str, ddl_type: str) -> None:
    """create_all() only creates whole tables that don't exist yet -- it never
    alters an existing table. This adds a single column via plain ALTER TABLE
    (supported by both SQLite and Postgres) only if it isn't there already, so
    it's safe to call on every startup regardless of environment."""
    existing = {c["name"] for c in inspect(engine).get_columns(table)}
    if column in existing:
        return
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl_type}"))


def init_db() -> None:
    import app.models  # noqa: F401  (ensures every model is registered on Base.metadata)

    Base.metadata.create_all(bind=engine)
    _add_column_if_missing("projects", "owner_id", "VARCHAR(32)")
