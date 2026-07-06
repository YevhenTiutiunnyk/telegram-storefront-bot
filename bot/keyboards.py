from __future__ import annotations

import os

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .db.models import CATEGORIES, Brand, CartItem, Model, Product
from .locales import LANG_NAMES, LANGS, t
from .utils import format_price

# Support contact is configurable via env so the code carries no hardcoded handle.
SUPPORT_USERNAME = (
    os.getenv("SUPPORT_USERNAME", "demo_support").strip().lstrip("@") or "demo_support"
)
SUPPORT_URL = f"https://t.me/{SUPPORT_USERNAME}"


def _support_button(lang: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=t("support", lang), url=SUPPORT_URL)


def _with_support(markup: InlineKeyboardMarkup, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=list(markup.inline_keyboard) + [[_support_button(lang)]]
    )


def language_kb(lang: str = "en") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code in LANGS:
        kb.button(text=LANG_NAMES[code], callback_data=f"lang:{code}")
    kb.adjust(2)
    return _with_support(kb.as_markup(), lang)


def checkout_method_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("delivery_mail", lang), callback_data="co:mail")
    kb.button(text=t("delivery_pickup", lang), callback_data="co:pickup")
    kb.button(text=t("cancel", lang), callback_data="cart:open")
    kb.adjust(1)
    return _with_support(kb.as_markup(), lang)


def checkout_pickup_city_kb(lang: str, city: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("pickup_city_main", lang, city=city), callback_data="co:city:main")
    kb.button(text=t("pickup_city_nearby", lang), callback_data="co:city:near")
    kb.button(text=t("cancel", lang), callback_data="cart:open")
    kb.adjust(1)
    return _with_support(kb.as_markup(), lang)


def main_menu_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("menu_catalog", lang), callback_data="cat:b")
    kb.button(text=t("menu_cart", lang), callback_data="cart:open")
    kb.button(text=t("menu_change_language", lang), callback_data="cfg:lang")
    kb.adjust(1)
    return _with_support(kb.as_markup(), lang)


def categories_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cat in CATEGORIES:
        kb.button(text=t(f"cat_{cat}", lang), callback_data=f"cat:cat:{cat}")
    kb.button(text=t("menu_cart", lang), callback_data="cart:open")
    kb.button(text=t("back_to_menu", lang), callback_data="menu:home")
    kb.adjust(1)
    return _with_support(kb.as_markup(), lang)


def brands_kb(lang: str, brands: list[Brand]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for b in brands:
        kb.button(text=b.name, callback_data=f"cat:m:{b.id}")
    kb.button(text=t("menu_cart", lang), callback_data="cart:open")
    kb.button(text=t("back_to_categories", lang), callback_data="cat:b")
    kb.adjust(1)
    return _with_support(kb.as_markup(), lang)


def models_kb(lang: str, category: str, models: list[Model]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for m in models:
        kb.button(text=m.name, callback_data=f"cat:v:{m.id}")
    kb.button(text=t("menu_cart", lang), callback_data="cart:open")
    kb.button(text=t("back_to_brands", lang), callback_data=f"cat:cat:{category}")
    kb.adjust(1)
    return _with_support(kb.as_markup(), lang)


def products_list_kb(
    lang: str, brand_id: int, products: list[Product]
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(
            text=f"{p.name} — €{format_price(p.price_cents)}",
            callback_data=f"cat:prod:{p.id}",
        )
    kb.button(text=t("menu_cart", lang), callback_data="cart:open")
    kb.button(text=t("back_to_models", lang), callback_data=f"cat:m:{brand_id}")
    kb.adjust(1)
    return _with_support(kb.as_markup(), lang)


def product_detail_kb(
    lang: str, product_id: int, model_id: int, qty: int
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text="−", callback_data=f"qty:{product_id}:{max(1, qty - 1)}"
        ),
        InlineKeyboardButton(
            text=t("qty_label", lang, qty=qty), callback_data="qty:noop"
        ),
        InlineKeyboardButton(text="+", callback_data=f"qty:{product_id}:{qty + 1}"),
    )
    kb.row(
        InlineKeyboardButton(
            text=t("add_to_cart", lang), callback_data=f"add:{product_id}:{qty}"
        )
    )
    kb.row(
        InlineKeyboardButton(text=t("menu_cart", lang), callback_data="cart:open"),
        InlineKeyboardButton(
            text=t("back_to_models", lang) if model_id else t("back", lang),
            callback_data=f"cat:v:{model_id}",
        ),
    )
    return _with_support(kb.as_markup(), lang)


def cart_kb(lang: str, items: list[CartItem]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for item in items:
        kb.button(
            text=t("cart_remove", lang, name=item.product.name),
            callback_data=f"cart:del:{item.id}",
        )
    if items:
        kb.button(text=t("cart_checkout", lang), callback_data="cart:checkout")
    kb.button(text=t("menu_catalog", lang), callback_data="cat:b")
    kb.button(text=t("back_to_menu", lang), callback_data="menu:home")
    kb.adjust(1)
    return _with_support(kb.as_markup(), lang)


# ---------- admin ----------


def admin_menu_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("admin_view_catalog", lang), callback_data="adm:view:b")
    kb.button(text=t("admin_add_product", lang), callback_data="adm:add")
    kb.button(text=t("admin_recent_orders", lang), callback_data="adm:orders")
    kb.adjust(1)
    return _with_support(kb.as_markup(), lang)


def admin_brands_kb(lang: str, brands: list[Brand]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for b in brands:
        kb.row(
            InlineKeyboardButton(text=b.name, callback_data=f"adm:view:m:{b.id}"),
            InlineKeyboardButton(
                text=t("admin_edit", lang), callback_data=f"adm:edit:brand:{b.id}"
            ),
            InlineKeyboardButton(
                text=t("admin_delete", lang), callback_data=f"adm:del:brand:{b.id}"
            ),
        )
    kb.row(InlineKeyboardButton(text=t("back", lang), callback_data="adm:menu"))
    return _with_support(kb.as_markup(), lang)


def admin_models_kb(
    lang: str, brand_id: int, models: list[Model]
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for m in models:
        kb.row(
            InlineKeyboardButton(text=m.name, callback_data=f"adm:view:v:{m.id}"),
            InlineKeyboardButton(
                text=t("admin_edit", lang), callback_data=f"adm:edit:model:{m.id}"
            ),
            InlineKeyboardButton(
                text=t("admin_delete", lang), callback_data=f"adm:del:model:{m.id}"
            ),
        )
    kb.row(InlineKeyboardButton(text=t("back", lang), callback_data="adm:view:b"))
    return _with_support(kb.as_markup(), lang)


def admin_products_kb(
    lang: str, model_id: int, brand_id: int, products: list[Product]
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for p in products:
        label = f"{p.name} — €{format_price(p.price_cents)}"
        kb.row(
            InlineKeyboardButton(text=label, callback_data=f"adm:edit:product:{p.id}")
        )
        kb.row(
            InlineKeyboardButton(
                text=t("admin_edit", lang), callback_data=f"adm:edit:product:{p.id}"
            ),
            InlineKeyboardButton(
                text=t("admin_delete", lang), callback_data=f"adm:del:product:{p.id}"
            ),
        )
    kb.row(
        InlineKeyboardButton(text=t("back", lang), callback_data=f"adm:view:m:{brand_id}")
    )
    return _with_support(kb.as_markup(), lang)


def admin_pick_category_kb(lang: str, prefix: str) -> InlineKeyboardMarkup:
    """`prefix` e.g. 'addp:cat' or 'adm:view:cat' → callbacks like addp:cat:<category>."""
    kb = InlineKeyboardBuilder()
    for cat in CATEGORIES:
        kb.button(text=t(f"cat_{cat}", lang), callback_data=f"{prefix}:{cat}")
    kb.button(text=t("cancel", lang), callback_data="adm:menu")
    kb.adjust(1)
    return _with_support(kb.as_markup(), lang)


def admin_pick_brand_kb(
    lang: str, brands: list[Brand], prefix: str
) -> InlineKeyboardMarkup:
    """`prefix` e.g. 'addp:brand' → callbacks like addp:brand:<id> or addp:brand:new."""
    kb = InlineKeyboardBuilder()
    for b in brands:
        kb.button(text=b.name, callback_data=f"{prefix}:{b.id}")
    kb.button(text=t("admin_new_brand", lang), callback_data=f"{prefix}:new")
    kb.button(text=t("cancel", lang), callback_data="adm:menu")
    kb.adjust(1)
    return _with_support(kb.as_markup(), lang)


def admin_pick_model_kb(
    lang: str, models: list[Model], prefix: str
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for m in models:
        kb.button(text=m.name, callback_data=f"{prefix}:{m.id}")
    kb.button(text=t("admin_new_model", lang), callback_data=f"{prefix}:new")
    kb.button(text=t("cancel", lang), callback_data="adm:menu")
    kb.adjust(1)
    return _with_support(kb.as_markup(), lang)


def admin_confirm_delete_kb(
    lang: str, entity: str, entity_id: int
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=t("admin_confirm_yes", lang),
        callback_data=f"adm:delok:{entity}:{entity_id}",
    )
    kb.button(text=t("admin_confirm_no", lang), callback_data="adm:menu")
    kb.adjust(2)
    return _with_support(kb.as_markup(), lang)


def admin_edit_field_kb(
    lang: str, entity: str, entity_id: int
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    fields: list[tuple[str, str]] = [("name", "admin_edit_name")]
    if entity in ("brand", "model", "product"):
        fields.append(("description", "admin_edit_description"))
    if entity in ("model", "product"):
        fields.append(("photo", "admin_edit_photo"))
    if entity == "product":
        fields.append(("price", "admin_edit_price"))
    for field, label_key in fields:
        kb.button(
            text=t(label_key, lang),
            callback_data=f"adm:editf:{entity}:{entity_id}:{field}",
        )
    kb.button(text=t("cancel", lang), callback_data="adm:menu")
    kb.adjust(2)
    return _with_support(kb.as_markup(), lang)


def admin_orders_kb(lang: str, orders) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for o in orders:
        kb.button(
            text=f"#{o.id} — €{format_price(o.total_cents)}",
            callback_data=f"adm:order:{o.id}",
        )
    kb.button(text=t("back", lang), callback_data="adm:menu")
    kb.adjust(1)
    return _with_support(kb.as_markup(), lang)


def admin_skip_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("cancel", lang), callback_data="adm:menu")
    return _with_support(kb.as_markup(), lang)
