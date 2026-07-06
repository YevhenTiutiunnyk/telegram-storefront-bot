import sqlite3

from bot.db.models import CATEGORIES


def _columns(db_path, table):
    con = sqlite3.connect(db_path)
    try:
        rows = con.execute(f"PRAGMA table_info({table})").fetchall()
    finally:
        con.close()
    return {r[1] for r in rows}


def _unique_index_columns(db_path, table):
    con = sqlite3.connect(db_path)
    try:
        result = []
        for idx in con.execute(f"PRAGMA index_list({table})").fetchall():
            idx_name, unique = idx[1], idx[2]
            if unique:
                cols = [r[2] for r in con.execute(f"PRAGMA index_info({idx_name})").fetchall()]
                result.append(cols)
    finally:
        con.close()
    return result


def test_categories_constant():
    assert CATEGORIES == ("coffee", "tea", "equipment", "accessories")


async def test_fresh_schema_has_new_columns(db):
    assert "category" in _columns(db, "brands")
    assert "description" in _columns(db, "brands")
    assert "description" in _columns(db, "models")


async def test_fresh_schema_brand_unique_is_name_and_category(db):
    unique_cols = _unique_index_columns(db, "brands")
    assert ["name", "category"] in unique_cols
    assert ["name"] not in unique_cols


async def test_fresh_schema_has_products_table(db):
    assert "price_cents" in _columns(db, "products")
    assert "product_name" in _columns(db, "order_items")
    assert "product_id" in _columns(db, "cart_items")
