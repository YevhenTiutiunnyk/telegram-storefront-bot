from bot.db import base, repo


async def test_db_fixture_initialises(db):
    async with repo.db_session() as session:
        brands = await repo.list_brands(session)
    assert brands == []
