from bot.db import repo


async def test_create_brand_with_category_and_description(db):
    async with repo.db_session() as session:
        brand = await repo.create_brand(session, "Blue Bottle", "coffee", "single-origin")
        bid = brand.id
    async with repo.db_session() as session:
        got = await repo.get_brand(session, bid)
        assert got.category == "coffee"
        assert got.description == "single-origin"


async def test_list_brands_filters_by_category(db):
    async with repo.db_session() as session:
        await repo.create_brand(session, "Blue Bottle", "coffee", None)
        await repo.create_brand(session, "Rare Tea Co", "tea", None)
    async with repo.db_session() as session:
        coffee = await repo.list_brands(session, "coffee")
        tea = await repo.list_brands(session, "tea")
    assert [b.name for b in coffee] == ["Blue Bottle"]
    assert [b.name for b in tea] == ["Rare Tea Co"]


async def test_same_brand_name_across_categories(db):
    async with repo.db_session() as session:
        await repo.create_brand(session, "House Blend", "coffee", None)
        await repo.create_brand(session, "House Blend", "tea", None)
    async with repo.db_session() as session:
        assert len(await repo.list_brands(session, "coffee")) == 1
        assert len(await repo.list_brands(session, "tea")) == 1


async def test_create_model_with_description(db):
    async with repo.db_session() as session:
        brand = await repo.create_brand(session, "Blue Bottle", "coffee", None)
        model = await repo.create_model(session, brand.id, "Bella Donovan", None, "chocolatey")
        mid = model.id
    async with repo.db_session() as session:
        got = await repo.get_model(session, mid)
        assert got.description == "chocolatey"


async def test_create_and_list_products(db):
    async with repo.db_session() as session:
        brand = await repo.create_brand(session, "Blue Bottle", "coffee", None)
        model = await repo.create_model(session, brand.id, "Bella Donovan", None, None)
        await repo.create_product(session, model.id, "Whole bean 250g", "chocolatey", 1500, None)
        mid = model.id
    async with repo.db_session() as session:
        products = await repo.list_products(session, mid)
    assert [(p.name, p.price_cents) for p in products] == [("Whole bean 250g", 1500)]


async def test_update_brand_and_model_description(db):
    async with repo.db_session() as session:
        brand = await repo.create_brand(session, "Blue Bottle", "coffee", None)
        model = await repo.create_model(session, brand.id, "Bella Donovan", None, None)
        bid, mid = brand.id, model.id
    async with repo.db_session() as session:
        await repo.update_brand(session, bid, description="new b desc")
        await repo.update_model(session, mid, description="new m desc")
    async with repo.db_session() as session:
        assert (await repo.get_brand(session, bid)).description == "new b desc"
        assert (await repo.get_model(session, mid)).description == "new m desc"
