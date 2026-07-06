from bot import keyboards as kb
from bot.db.models import Brand, Model


def _callbacks(markup):
    return [btn.callback_data for row in markup.inline_keyboard for btn in row if btn.callback_data]


def test_categories_kb_has_all_four():
    markup = kb.categories_kb("en")
    cbs = _callbacks(markup)
    assert "cat:cat:coffee" in cbs
    assert "cat:cat:tea" in cbs
    assert "cat:cat:equipment" in cbs
    assert "cat:cat:accessories" in cbs


def test_brands_kb_back_goes_to_categories():
    brands = [Brand(id=1, name="Blue Bottle", category="coffee")]
    cbs = _callbacks(kb.brands_kb("en", brands))
    assert "cat:m:1" in cbs
    assert "cat:b" in cbs  # back to category picker


def test_models_kb_back_goes_to_category():
    models = [Model(id=7, brand_id=1, name="Bella Donovan")]
    cbs = _callbacks(kb.models_kb("en", "coffee", models))
    assert "cat:v:7" in cbs
    assert "cat:cat:coffee" in cbs  # back to that category's brand list


def test_admin_pick_category_kb_prefix():
    cbs = _callbacks(kb.admin_pick_category_kb("en", "addp:cat"))
    assert "addp:cat:coffee" in cbs
    assert "addp:cat:accessories" in cbs


def test_admin_edit_field_kb_brand_has_description():
    cbs = _callbacks(kb.admin_edit_field_kb("en", "brand", 3))
    assert "adm:editf:brand:3:description" in cbs


def test_admin_edit_field_kb_model_has_description():
    cbs = _callbacks(kb.admin_edit_field_kb("en", "model", 4))
    assert "adm:editf:model:4:description" in cbs


def test_admin_edit_field_kb_product_has_price():
    cbs = _callbacks(kb.admin_edit_field_kb("en", "product", 5))
    assert "adm:editf:product:5:price" in cbs
