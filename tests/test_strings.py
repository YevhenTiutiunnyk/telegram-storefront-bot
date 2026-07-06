from bot.locales.strings import LANGS, STRINGS
from bot.db.models import CATEGORIES

NEW_KEYS = [
    "choose_category",
    "no_brands_in_category",
    "back_to_categories",
    "admin_ask_brand_description",
    "admin_ask_model_description",
] + [f"cat_{c}" for c in CATEGORIES]


def test_new_keys_exist_in_all_languages():
    for key in NEW_KEYS:
        assert key in STRINGS, f"missing key {key}"
        for lang in LANGS:
            assert STRINGS[key].get(lang), f"{key} missing {lang}"


def test_add_product_label_is_generic():
    # The admin UI uses domain-neutral wording.
    assert STRINGS["admin_add_product"]["en"] == "➕ Add product"


def test_every_key_has_english():
    for key, entry in STRINGS.items():
        assert entry.get("en"), f"{key} missing English"
