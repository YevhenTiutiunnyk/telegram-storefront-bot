from __future__ import annotations

from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine(db_path: str) -> None:
    global _engine, _session_factory
    _engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", future=True)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


def _column_names(conn: Connection, table: str) -> set[str]:
    rows = conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()
    return {row[1] for row in rows}


def _unique_index_columns(conn: Connection, table: str) -> list[list[str]]:
    out: list[list[str]] = []
    for idx in conn.exec_driver_sql(f"PRAGMA index_list({table})").fetchall():
        idx_name, unique = idx[1], idx[2]
        if unique:
            cols = [
                r[2]
                for r in conn.exec_driver_sql(f"PRAGMA index_info({idx_name})").fetchall()
            ]
            out.append(cols)
    return out


def _run_migrations(conn: Connection) -> None:
    """Idempotent in-place upgrade of the SQLite schema.

    Safe to run on a fresh DB (create_all already built the new schema -> no-op)
    and on a pre-feature DB (adds columns, backfills category='coffee', rebuilds
    the brand unique constraint). Preserves all existing rows.
    """
    brand_cols = _column_names(conn, "brands")
    if "category" not in brand_cols:
        conn.exec_driver_sql(
            "ALTER TABLE brands ADD COLUMN category VARCHAR(16) NOT NULL DEFAULT 'coffee'"
        )
    if "description" not in brand_cols:
        conn.exec_driver_sql("ALTER TABLE brands ADD COLUMN description VARCHAR(1024)")

    model_cols = _column_names(conn, "models")
    if "description" not in model_cols:
        conn.exec_driver_sql("ALTER TABLE models ADD COLUMN description VARCHAR(1024)")

    # Rebuild the brand unique constraint from UNIQUE(name) to UNIQUE(name, category)
    # only if the old single-column unique index is still present.
    unique = _unique_index_columns(conn, "brands")
    if ["name"] in unique and ["name", "category"] not in unique:
        # This rebuild DROPs and recreates `brands`. With SQLite foreign-key
        # enforcement ON, DROP TABLE performs an implicit DELETE that
        # cascade-deletes every model and product (total catalog loss). We rely
        # on enforcement being OFF — aiosqlite's default, which we never
        # override. `PRAGMA foreign_keys` cannot be changed inside a transaction
        # (it is a silent no-op there), so instead of pretending to toggle it we
        # read it and refuse loudly if a future connect-time
        # `PRAGMA foreign_keys=ON` ever turns enforcement on. Better a failed
        # migration than lost data.
        if conn.exec_driver_sql("PRAGMA foreign_keys").scalar():
            raise RuntimeError(
                "Refusing to rebuild `brands`: SQLite foreign-key enforcement "
                "is ON, which would cascade-delete all models and products. Run "
                "this migration with foreign_keys=OFF."
            )
        conn.exec_driver_sql(
            """
            CREATE TABLE brands_new (
                id INTEGER NOT NULL PRIMARY KEY,
                name VARCHAR(128) NOT NULL,
                category VARCHAR(16) NOT NULL DEFAULT 'coffee',
                description VARCHAR(1024),
                UNIQUE (name, category)
            )
            """
        )
        conn.exec_driver_sql(
            "INSERT INTO brands_new (id, name, category, description) "
            "SELECT id, name, category, description FROM brands"
        )
        conn.exec_driver_sql("DROP TABLE brands")
        conn.exec_driver_sql("ALTER TABLE brands_new RENAME TO brands")
        # Loudly assert the rebuild left no dangling child references.
        violations = conn.exec_driver_sql("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise RuntimeError(
                f"Post-rebuild foreign-key check failed: {violations}"
            )


async def init_db(db_path: str) -> None:
    init_engine(db_path)
    assert _engine is not None
    # Import models so they register with Base.metadata before create_all
    from . import models  # noqa: F401

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_run_migrations)


def session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError("DB not initialised — call init_db() first")
    return _session_factory
