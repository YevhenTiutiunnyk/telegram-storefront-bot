from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..config import Config
from ..db import repo
from ..keyboards import (
    admin_brands_kb,
    admin_confirm_delete_kb,
    admin_edit_field_kb,
    admin_menu_kb,
    admin_models_kb,
    admin_orders_kb,
    admin_pick_brand_kb,
    admin_pick_category_kb,
    admin_pick_model_kb,
    admin_products_kb,
)
from ..locales import t
from ..states import AdminAddProduct, AdminEdit
from ..utils import format_order, format_price, is_admin

router = Router(name="admin")


async def _lang(telegram_id: int, username: str | None) -> str:
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(session, telegram_id, username)
        return user.language


def _guard(call: CallbackQuery, config: Config) -> bool:
    return is_admin(config, call.from_user.id)


# ---------- entry ----------


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext, config: Config) -> None:
    if not is_admin(config, message.from_user.id):
        lang = await _lang(message.from_user.id, message.from_user.username)
        await message.answer(t("admin_only", lang))
        return
    await state.clear()
    lang = await _lang(message.from_user.id, message.from_user.username)
    await message.answer(t("admin_menu", lang), reply_markup=admin_menu_kb(lang))


@router.callback_query(F.data == "adm:menu")
async def on_menu(call: CallbackQuery, state: FSMContext, config: Config) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    await state.clear()
    lang = await _lang(call.from_user.id, call.from_user.username)
    await call.answer()
    if call.message:
        await call.message.answer(t("admin_menu", lang), reply_markup=admin_menu_kb(lang))


# ---------- view ----------


@router.callback_query(F.data == "adm:view:b")
async def view_categories(call: CallbackQuery, config: Config) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    lang = await _lang(call.from_user.id, call.from_user.username)
    await call.answer()
    if call.message:
        await call.message.answer(
            t("choose_category", lang),
            reply_markup=admin_pick_category_kb(lang, "adm:view:cat"),
        )


@router.callback_query(F.data.startswith("adm:view:cat:"))
async def view_brands(call: CallbackQuery, config: Config) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    category = call.data.rsplit(":", 1)[1]
    lang = await _lang(call.from_user.id, call.from_user.username)
    async with repo.db_session() as session:
        brands = await repo.list_brands(session, category)
    await call.answer()
    if call.message:
        if not brands:
            await call.message.answer(t("no_brands_in_category", lang))
            return
        await call.message.answer(
            t("brands_title", lang), reply_markup=admin_brands_kb(lang, brands)
        )


@router.callback_query(F.data.startswith("adm:view:m:"))
async def view_models(call: CallbackQuery, config: Config) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    brand_id = int(call.data.rsplit(":", 1)[1])
    lang = await _lang(call.from_user.id, call.from_user.username)
    async with repo.db_session() as session:
        brand = await repo.get_brand(session, brand_id)
        models = await repo.list_models(session, brand_id)
    await call.answer()
    if not call.message or not brand:
        return
    if not models:
        await call.message.answer(t("no_models", lang))
        return
    await call.message.answer(
        t("models_title", lang, brand=brand.name),
        reply_markup=admin_models_kb(lang, brand_id, models),
    )


@router.callback_query(F.data.startswith("adm:view:v:"))
async def view_products(call: CallbackQuery, config: Config) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    model_id = int(call.data.rsplit(":", 1)[1])
    lang = await _lang(call.from_user.id, call.from_user.username)
    async with repo.db_session() as session:
        model = await repo.get_model(session, model_id)
        if not model:
            await call.answer()
            return
        brand_id = model.brand_id
        products = await repo.list_products(session, model_id)
    await call.answer()
    if not call.message:
        return
    if not products:
        await call.message.answer(t("no_products", lang))
        return
    await call.message.answer(
        t("products_title", lang, model=model.name),
        reply_markup=admin_products_kb(lang, model_id, brand_id, products),
    )


# ---------- delete ----------


@router.callback_query(F.data.startswith("adm:del:"))
async def confirm_delete(call: CallbackQuery, config: Config) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    _, _, entity, entity_id_s = call.data.split(":")
    entity_id = int(entity_id_s)
    lang = await _lang(call.from_user.id, call.from_user.username)
    name = ""
    async with repo.db_session() as session:
        if entity == "brand":
            obj = await repo.get_brand(session, entity_id)
            name = obj.name if obj else ""
        elif entity == "model":
            obj = await repo.get_model(session, entity_id)
            name = obj.name if obj else ""
        elif entity == "product":
            obj = await repo.get_product(session, entity_id)
            name = obj.name if obj else ""
    await call.answer()
    if call.message:
        await call.message.answer(
            t("admin_confirm_delete", lang, name=name),
            reply_markup=admin_confirm_delete_kb(lang, entity, entity_id),
        )


@router.callback_query(F.data.startswith("adm:delok:"))
async def do_delete(call: CallbackQuery, config: Config) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    _, _, entity, entity_id_s = call.data.split(":")
    entity_id = int(entity_id_s)
    lang = await _lang(call.from_user.id, call.from_user.username)
    async with repo.db_session() as session:
        if entity == "brand":
            await repo.delete_brand(session, entity_id)
        elif entity == "model":
            await repo.delete_model(session, entity_id)
        elif entity == "product":
            await repo.delete_product(session, entity_id)
    await call.answer(t("admin_deleted", lang))
    if call.message:
        await call.message.answer(t("admin_menu", lang), reply_markup=admin_menu_kb(lang))


# ---------- add product (FSM) ----------


@router.callback_query(F.data == "adm:add")
async def add_start(call: CallbackQuery, state: FSMContext, config: Config) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    await state.clear()
    lang = await _lang(call.from_user.id, call.from_user.username)
    await state.set_state(AdminAddProduct.pick_category)
    await call.answer()
    if call.message:
        await call.message.answer(
            t("choose_category", lang),
            reply_markup=admin_pick_category_kb(lang, "addp:cat"),
        )


@router.callback_query(AdminAddProduct.pick_category, F.data.startswith("addp:cat:"))
async def add_pick_category(
    call: CallbackQuery, state: FSMContext, config: Config
) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    category = call.data.rsplit(":", 1)[1]
    lang = await _lang(call.from_user.id, call.from_user.username)
    await state.update_data(category=category)
    async with repo.db_session() as session:
        brands = await repo.list_brands(session, category)
    await state.set_state(AdminAddProduct.pick_brand)
    await call.answer()
    if call.message:
        await call.message.answer(
            t("admin_add_pick_brand", lang),
            reply_markup=admin_pick_brand_kb(lang, brands, "addp:brand"),
        )


@router.callback_query(AdminAddProduct.pick_brand, F.data.startswith("addp:brand:"))
async def add_pick_brand(
    call: CallbackQuery, state: FSMContext, config: Config
) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    token = call.data.rsplit(":", 1)[1]
    lang = await _lang(call.from_user.id, call.from_user.username)
    if token == "new":
        await state.set_state(AdminAddProduct.new_brand_name)
        await call.answer()
        if call.message:
            await call.message.answer(t("admin_ask_brand_name", lang))
        return
    brand_id = int(token)
    await state.update_data(brand_id=brand_id)
    async with repo.db_session() as session:
        models = await repo.list_models(session, brand_id)
    await state.set_state(AdminAddProduct.pick_model)
    await call.answer()
    if call.message:
        await call.message.answer(
            t("admin_add_pick_model", lang),
            reply_markup=admin_pick_model_kb(lang, models, "addp:model"),
        )


@router.message(AdminAddProduct.new_brand_name, F.text)
async def add_new_brand_name(message: Message, state: FSMContext) -> None:
    await state.update_data(new_brand_name=message.text.strip())
    lang = await _lang(message.from_user.id, message.from_user.username)
    await state.set_state(AdminAddProduct.new_brand_description)
    await message.answer(t("admin_ask_brand_description", lang))


@router.message(AdminAddProduct.new_brand_description, Command("skip"))
async def add_new_brand_skip_description(message: Message, state: FSMContext) -> None:
    await _finalise_new_brand(message, state, None)


@router.message(AdminAddProduct.new_brand_description, F.text)
async def add_new_brand_description(message: Message, state: FSMContext) -> None:
    await _finalise_new_brand(message, state, message.text.strip())


async def _finalise_new_brand(
    message: Message, state: FSMContext, description: str | None
) -> None:
    data = await state.get_data()
    category = data["category"]
    name = data["new_brand_name"]
    lang = await _lang(message.from_user.id, message.from_user.username)
    async with repo.db_session() as session:
        brand = await repo.create_brand(session, name, category, description)
        brand_id = brand.id
    await state.update_data(brand_id=brand_id)
    await state.set_state(AdminAddProduct.pick_model)
    await message.answer(
        t("admin_add_pick_model", lang),
        reply_markup=admin_pick_model_kb(lang, [], "addp:model"),
    )


@router.callback_query(AdminAddProduct.pick_model, F.data.startswith("addp:model:"))
async def add_pick_model(
    call: CallbackQuery, state: FSMContext, config: Config
) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    token = call.data.rsplit(":", 1)[1]
    lang = await _lang(call.from_user.id, call.from_user.username)
    if token == "new":
        await state.set_state(AdminAddProduct.new_model_name)
        await call.answer()
        if call.message:
            await call.message.answer(t("admin_ask_model_name", lang))
        return
    model_id = int(token)
    await state.update_data(model_id=model_id)
    await state.set_state(AdminAddProduct.product_name)
    await call.answer()
    if call.message:
        await call.message.answer(t("admin_ask_product_name", lang))


@router.message(AdminAddProduct.new_model_name, F.text)
async def add_new_model_name(message: Message, state: FSMContext) -> None:
    await state.update_data(new_model_name=message.text.strip())
    lang = await _lang(message.from_user.id, message.from_user.username)
    await state.set_state(AdminAddProduct.new_model_photo)
    await message.answer(t("admin_ask_model_photo", lang))


@router.message(AdminAddProduct.new_model_photo, F.photo)
async def add_new_model_photo(message: Message, state: FSMContext) -> None:
    await state.update_data(new_model_photo=message.photo[-1].file_id)
    await _ask_new_model_description(message, state)


@router.message(AdminAddProduct.new_model_photo, Command("skip"))
async def add_new_model_skip_photo(message: Message, state: FSMContext) -> None:
    await state.update_data(new_model_photo=None)
    await _ask_new_model_description(message, state)


@router.message(AdminAddProduct.new_model_photo)
async def add_new_model_photo_invalid(message: Message, state: FSMContext) -> None:
    lang = await _lang(message.from_user.id, message.from_user.username)
    await message.answer(t("admin_send_photo_or_skip", lang))


async def _ask_new_model_description(message: Message, state: FSMContext) -> None:
    lang = await _lang(message.from_user.id, message.from_user.username)
    await state.set_state(AdminAddProduct.new_model_description)
    await message.answer(t("admin_ask_model_description", lang))


@router.message(AdminAddProduct.new_model_description, Command("skip"))
async def add_new_model_skip_description(message: Message, state: FSMContext) -> None:
    await _finalise_new_model(message, state, None)


@router.message(AdminAddProduct.new_model_description, F.text)
async def add_new_model_description(message: Message, state: FSMContext) -> None:
    await _finalise_new_model(message, state, message.text.strip())


async def _finalise_new_model(
    message: Message, state: FSMContext, description: str | None
) -> None:
    data = await state.get_data()
    brand_id = int(data["brand_id"])
    name = data["new_model_name"]
    photo_id = data.get("new_model_photo")
    lang = await _lang(message.from_user.id, message.from_user.username)
    async with repo.db_session() as session:
        model = await repo.create_model(session, brand_id, name, photo_id, description)
        model_id = model.id
    await state.update_data(model_id=model_id)
    await state.set_state(AdminAddProduct.product_name)
    await message.answer(t("admin_ask_product_name", lang))


@router.message(AdminAddProduct.product_name, F.text)
async def add_product_name(message: Message, state: FSMContext) -> None:
    await state.update_data(product_name=message.text.strip())
    lang = await _lang(message.from_user.id, message.from_user.username)
    await state.set_state(AdminAddProduct.product_price)
    await message.answer(t("admin_ask_product_price", lang))


def _parse_price_to_cents(raw: str) -> int | None:
    raw = raw.strip().replace(",", ".").replace("€", "").strip()
    try:
        value = float(raw)
    except ValueError:
        return None
    if value < 0:
        return None
    return round(value * 100)


@router.message(AdminAddProduct.product_price, F.text)
async def add_product_price(message: Message, state: FSMContext) -> None:
    lang = await _lang(message.from_user.id, message.from_user.username)
    cents = _parse_price_to_cents(message.text or "")
    if cents is None:
        await message.answer(t("admin_invalid_price", lang))
        return
    await state.update_data(price_cents=cents)
    await state.set_state(AdminAddProduct.product_description)
    await message.answer(t("admin_ask_product_description", lang))


@router.message(AdminAddProduct.product_description, Command("skip"))
async def add_product_skip_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=None)
    lang = await _lang(message.from_user.id, message.from_user.username)
    await state.set_state(AdminAddProduct.product_photo)
    await message.answer(t("admin_ask_product_photo", lang))


@router.message(AdminAddProduct.product_description, F.text)
async def add_product_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text.strip())
    lang = await _lang(message.from_user.id, message.from_user.username)
    await state.set_state(AdminAddProduct.product_photo)
    await message.answer(t("admin_ask_product_photo", lang))


@router.message(AdminAddProduct.product_photo, F.photo)
async def add_product_photo(message: Message, state: FSMContext) -> None:
    await _finalise_product(message, state, message.photo[-1].file_id)


@router.message(AdminAddProduct.product_photo, Command("skip"))
async def add_product_skip_photo(message: Message, state: FSMContext) -> None:
    await _finalise_product(message, state, None)


@router.message(AdminAddProduct.product_photo)
async def add_product_photo_invalid(message: Message, state: FSMContext) -> None:
    lang = await _lang(message.from_user.id, message.from_user.username)
    await message.answer(t("admin_send_photo_or_skip", lang))


async def _finalise_product(
    message: Message, state: FSMContext, photo_id: str | None
) -> None:
    data = await state.get_data()
    lang = await _lang(message.from_user.id, message.from_user.username)
    async with repo.db_session() as session:
        product = await repo.create_product(
            session,
            model_id=int(data["model_id"]),
            name=data["product_name"],
            description=data.get("description"),
            price_cents=int(data["price_cents"]),
            photo_file_id=photo_id,
        )
        model = await repo.get_model(session, product.model_id)
        brand = await repo.get_brand(session, model.brand_id) if model else None
    await state.clear()
    await message.answer(
        t(
            "admin_product_added",
            lang,
            name=data["product_name"],
            price=format_price(int(data["price_cents"])),
            brand=brand.name if brand else "?",
            model=model.name if model else "?",
        ),
        reply_markup=admin_menu_kb(lang),
    )


# ---------- edit ----------


@router.callback_query(F.data.startswith("adm:edit:"))
async def edit_pick_field(
    call: CallbackQuery, state: FSMContext, config: Config
) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    _, _, entity, entity_id_s = call.data.split(":")
    entity_id = int(entity_id_s)
    lang = await _lang(call.from_user.id, call.from_user.username)
    await state.clear()
    await call.answer()
    if call.message:
        await call.message.answer(
            t("admin_edit_field", lang),
            reply_markup=admin_edit_field_kb(lang, entity, entity_id),
        )


@router.callback_query(F.data.startswith("adm:editf:"))
async def edit_ask_value(
    call: CallbackQuery, state: FSMContext, config: Config
) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    _, _, entity, entity_id_s, field = call.data.split(":")
    entity_id = int(entity_id_s)
    lang = await _lang(call.from_user.id, call.from_user.username)
    await state.update_data(entity=entity, entity_id=entity_id, field=field)
    if field == "photo":
        await state.set_state(AdminEdit.awaiting_photo)
        await call.answer()
        if call.message:
            await call.message.answer(t("admin_ask_model_photo", lang))
    else:
        await state.set_state(AdminEdit.awaiting_value)
        await call.answer()
        if call.message:
            await call.message.answer(t("admin_send_new_value", lang))


@router.message(AdminEdit.awaiting_value, F.text)
async def edit_save_value(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    entity = data["entity"]
    entity_id = int(data["entity_id"])
    field = data["field"]
    value = message.text.strip()
    lang = await _lang(message.from_user.id, message.from_user.username)

    async with repo.db_session() as session:
        if entity == "brand":
            if field == "name":
                await repo.update_brand(session, entity_id, name=value)
            elif field == "description":
                await repo.update_brand(session, entity_id, description=value)
        elif entity == "model":
            if field == "name":
                await repo.update_model(session, entity_id, name=value)
            elif field == "description":
                await repo.update_model(session, entity_id, description=value)
        elif entity == "product":
            if field == "name":
                await repo.update_product(session, entity_id, name=value)
            elif field == "description":
                await repo.update_product(session, entity_id, description=value)
            elif field == "price":
                cents = _parse_price_to_cents(value)
                if cents is None:
                    await message.answer(t("admin_invalid_price", lang))
                    return
                await repo.update_product(session, entity_id, price_cents=cents)
    await state.clear()
    await message.answer(t("admin_updated", lang), reply_markup=admin_menu_kb(lang))


@router.message(AdminEdit.awaiting_photo, F.photo)
async def edit_save_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    entity = data["entity"]
    entity_id = int(data["entity_id"])
    photo_id = message.photo[-1].file_id
    lang = await _lang(message.from_user.id, message.from_user.username)
    async with repo.db_session() as session:
        if entity == "model":
            await repo.update_model(session, entity_id, photo_file_id=photo_id)
        elif entity == "product":
            await repo.update_product(session, entity_id, photo_file_id=photo_id)
    await state.clear()
    await message.answer(t("admin_updated", lang), reply_markup=admin_menu_kb(lang))


@router.message(AdminEdit.awaiting_photo)
async def edit_photo_invalid(message: Message, state: FSMContext) -> None:
    lang = await _lang(message.from_user.id, message.from_user.username)
    await message.answer(t("admin_send_photo_or_skip", lang))


# ---------- orders ----------


@router.callback_query(F.data == "adm:orders")
async def show_orders(call: CallbackQuery, config: Config) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    lang = await _lang(call.from_user.id, call.from_user.username)
    async with repo.db_session() as session:
        orders = await repo.recent_orders(session, limit=20)
    await call.answer()
    if not call.message:
        return
    if not orders:
        await call.message.answer(t("admin_no_orders", lang))
        return
    await call.message.answer(
        t("admin_orders_header", lang, n=len(orders)),
        reply_markup=admin_orders_kb(lang, orders),
    )


@router.callback_query(F.data.startswith("adm:order:"))
async def show_order(call: CallbackQuery, config: Config) -> None:
    if not _guard(call, config):
        await call.answer()
        return
    order_id = int(call.data.rsplit(":", 1)[1])
    async with repo.db_session() as session:
        order = await repo.get_order(session, order_id)
    await call.answer()
    if not call.message or not order:
        return
    await call.message.answer(format_order(order))
