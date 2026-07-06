from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from ..db import repo
from ..keyboards import (
    brands_kb,
    categories_kb,
    models_kb,
    product_detail_kb,
    products_list_kb,
)
from ..locales import t
from ..utils import format_price

router = Router(name="catalog")


@router.callback_query(F.data == "cat:b")
async def show_categories(call: CallbackQuery) -> None:
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        lang = user.language
    await call.answer()
    if call.message:
        await call.message.answer(
            t("choose_category", lang), reply_markup=categories_kb(lang)
        )


@router.callback_query(F.data.startswith("cat:cat:"))
async def show_brands(call: CallbackQuery) -> None:
    category = call.data.rsplit(":", 1)[1]
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        lang = user.language
        brands = await repo.list_brands(session, category)

    await call.answer()
    if not call.message:
        return
    if not brands:
        await call.message.answer(t("no_brands_in_category", lang))
        return
    await call.message.answer(
        t("brands_title", lang), reply_markup=brands_kb(lang, brands)
    )


@router.callback_query(F.data.startswith("cat:m:"))
async def show_models(call: CallbackQuery) -> None:
    brand_id = int(call.data.rsplit(":", 1)[1])
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        lang = user.language
        brand = await repo.get_brand(session, brand_id)
        models = await repo.list_models(session, brand_id)
        category = brand.category if brand else "coffee"
        brand_name = brand.name if brand else ""
        brand_desc = brand.description if brand else None

    await call.answer()
    if not call.message or not brand:
        return
    if not models:
        await call.message.answer(t("no_models", lang))
        return
    title = t("models_title", lang, brand=brand_name)
    if brand_desc:
        title = f"{title}\n\n{brand_desc}"
    await call.message.answer(title, reply_markup=models_kb(lang, category, models))


@router.callback_query(F.data.startswith("cat:v:"))
async def show_products(call: CallbackQuery) -> None:
    model_id = int(call.data.rsplit(":", 1)[1])
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        lang = user.language
        model = await repo.get_model(session, model_id)
        products = await repo.list_products(session, model_id)
        brand_id = model.brand_id if model else 0
        model_name = model.name if model else ""
        model_desc = model.description if model else None
        model_photo = model.photo_file_id if model else None

    await call.answer()
    if not call.message or not model:
        return
    title = t("products_title", lang, model=model_name)
    if model_desc:
        title = f"{title}\n\n{model_desc}"
    if model_photo:
        await call.message.answer_photo(
            photo=model_photo,
            caption=title,
            reply_markup=products_list_kb(lang, brand_id, products) if products else None,
        )
    else:
        await call.message.answer(
            title,
            reply_markup=products_list_kb(lang, brand_id, products) if products else None,
        )
    if not products:
        await call.message.answer(t("no_products", lang))


@router.callback_query(F.data.startswith("cat:prod:"))
async def show_product_detail(call: CallbackQuery) -> None:
    product_id = int(call.data.rsplit(":", 1)[1])
    await _send_product_card(call, product_id, qty=1, replace=False)


@router.callback_query(F.data.startswith("qty:"))
async def on_qty_change(call: CallbackQuery) -> None:
    parts = call.data.split(":")
    if len(parts) == 2 and parts[1] == "noop":
        await call.answer()
        return
    if len(parts) != 3:
        await call.answer()
        return
    product_id = int(parts[1])
    qty = max(1, int(parts[2]))
    await _send_product_card(call, product_id, qty=qty, replace=True)


@router.callback_query(F.data.startswith("add:"))
async def on_add_to_cart(call: CallbackQuery) -> None:
    _, product_id_s, qty_s = call.data.split(":")
    product_id = int(product_id_s)
    qty = max(1, int(qty_s))
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        lang = user.language
        product = await repo.get_product(session, product_id)
        if product is None:
            await call.answer()
            return
        await repo.add_to_cart(session, user.id, product.id, qty)
        name = product.name

    await call.answer(t("added_to_cart", lang, name=name, qty=qty), show_alert=False)


async def _send_product_card(
    call: CallbackQuery, product_id: int, qty: int, *, replace: bool
) -> None:
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        lang = user.language
        product = await repo.get_product(session, product_id)
        if product is None:
            await call.answer()
            return
        model_id = product.model_id
        name = product.name
        price_cents = product.price_cents
        description = product.description
        photo_file_id = product.photo_file_id

    caption = t(
        "product_caption",
        lang,
        name=name,
        price=format_price(price_cents),
        description=description or "",
    )
    kb = product_detail_kb(lang, product_id, model_id, qty)

    await call.answer()
    if not call.message:
        return

    if replace and call.message.photo:
        # Edit existing photo card (caption + markup); keep photo as-is
        try:
            await call.message.edit_caption(caption=caption, reply_markup=kb, parse_mode="HTML")
            return
        except Exception:
            pass
    if replace and not call.message.photo:
        try:
            await call.message.edit_text(caption, reply_markup=kb, parse_mode="HTML")
            return
        except Exception:
            pass

    if photo_file_id:
        await call.message.answer_photo(
            photo=photo_file_id, caption=caption, reply_markup=kb, parse_mode="HTML"
        )
    else:
        await call.message.answer(caption, reply_markup=kb, parse_mode="HTML")
