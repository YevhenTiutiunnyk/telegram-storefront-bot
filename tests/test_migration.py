import sqlite3

import pytest
from sqlalchemy import create_engine, event

from bot.db import base


def _make_old_db(path):
    """Recreate the pre-feature schema with seed rows."""
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE brands (
            id INTEGER NOT NULL PRIMARY KEY,
            name VARCHAR(128) NOT NULL,
            UNIQUE (name)
        );
        CREATE TABLE models (
            id INTEGER NOT NULL PRIMARY KEY,
            brand_id INTEGER NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
            name VARCHAR(128) NOT NULL,
            photo_file_id VARCHAR(256)
        );
        CREATE TABLE products (
            id INTEGER NOT NULL PRIMARY KEY,
            model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
            name VARCHAR(128) NOT NULL,
            description VARCHAR(1024),
            price_cents INTEGER NOT NULL,
            photo_file_id VARCHAR(256)
        );
        INSERT INTO brands (id, name) VALUES (1, 'Blue Bottle'), (2, 'Stumptown');
        INSERT INTO models (id, brand_id, name) VALUES (1, 1, 'Bella Donovan'), (2, 2, 'Hair Bender');
        INSERT INTO products (id, model_id, name, description, price_cents)
            VALUES (1, 1, 'Whole bean 250g', 'chocolatey', 1500);
        """
    )
    con.commit()
    con.close()


def _columns(path, table):
    con = sqlite3.connect(path)
    try:
        return {r[1] for r in con.execute(f"PRAGMA table_info({table})").fetchall()}
    finally:
        con.close()


def _unique_index_columns(path, table):
    con = sqlite3.connect(path)
    try:
        out = []
        for idx in con.execute(f"PRAGMA index_list({table})").fetchall():
            if idx[2]:
                cols = [r[2] for r in con.execute(f"PRAGMA index_info({idx[1]})").fetchall()]
                out.append(cols)
        return out
    finally:
        con.close()


def _query(path, sql):
    con = sqlite3.connect(path)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


async def test_migration_preserves_data_and_upgrades_schema(tmp_path):
    db_file = str(tmp_path / "old.db")
    _make_old_db(db_file)

    await base.init_db(db_file)
    await base._engine.dispose()

    # New columns exist
    assert "category" in _columns(db_file, "brands")
    assert "description" in _columns(db_file, "brands")
    assert "description" in _columns(db_file, "models")

    # All existing brands defaulted to 'coffee'
    rows = _query(db_file, "SELECT name, category FROM brands ORDER BY id")
    assert rows == [("Blue Bottle", "coffee"), ("Stumptown", "coffee")]

    # Models + products intact
    assert _query(db_file, "SELECT COUNT(*) FROM models")[0][0] == 2
    assert _query(db_file, "SELECT name, price_cents FROM products")[0] == (
        "Whole bean 250g",
        1500,
    )

    # Unique constraint rebuilt to (name, category)
    unique = _unique_index_columns(db_file, "brands")
    assert ["name", "category"] in unique
    assert ["name"] not in unique


async def test_migration_is_idempotent(tmp_path):
    db_file = str(tmp_path / "old.db")
    _make_old_db(db_file)

    await base.init_db(db_file)
    await base._engine.dispose()
    # Run a second time against the already-migrated DB
    await base.init_db(db_file)
    await base._engine.dispose()

    rows = _query(db_file, "SELECT name, category FROM brands ORDER BY id")
    assert rows == [("Blue Bottle", "coffee"), ("Stumptown", "coffee")]
    assert _query(db_file, "SELECT COUNT(*) FROM products")[0][0] == 1


def test_brand_rebuild_refuses_when_fk_enforcement_on(tmp_path):
    """If a future connect-time PRAGMA turns FK enforcement on, the destructive
    brand-table rebuild must refuse and roll back rather than cascade-delete the
    entire catalog. Drives _run_migrations through a sync engine whose connect
    listener enables foreign_keys (the exact landmine the guard protects against)."""
    db_file = str(tmp_path / "old.db")
    _make_old_db(db_file)

    engine = create_engine(f"sqlite:///{db_file}")

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_conn, _):  # FK on at connect time => effective inside txn
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    try:
        with pytest.raises(RuntimeError, match="foreign-key enforcement is ON"):
            with engine.begin() as conn:
                assert conn.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1
                base._run_migrations(conn)
    finally:
        engine.dispose()

    # The raise rolled back the transaction: catalog fully intact, old schema kept.
    assert _query(db_file, "SELECT COUNT(*) FROM brands")[0][0] == 2
    assert _query(db_file, "SELECT COUNT(*) FROM models")[0][0] == 2
    assert _query(db_file, "SELECT COUNT(*) FROM products")[0][0] == 1
    unique = _unique_index_columns(db_file, "brands")
    assert ["name"] in unique
