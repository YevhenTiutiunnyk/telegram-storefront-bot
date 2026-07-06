from __future__ import annotations

import pytest_asyncio

from bot.db import base


@pytest_asyncio.fixture
async def db(tmp_path):
    """Fresh, migrated SQLite DB per test. Yields the db file path."""
    db_file = tmp_path / "test.db"
    await base.init_db(str(db_file))
    yield str(db_file)
    if base._engine is not None:
        await base._engine.dispose()
    base._engine = None
    base._session_factory = None
