from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..config import Config
from ..db import repo
from ..keyboards import (
    cart_kb,
    checkout_method_kb,
    checkout_pickup_city_kb,
    main_menu_kb,
)
from ..locales import t
from ..states import Checkout
from ..utils import (
    PICKUP_MIN_ORDER_CENTS,
    format_order,
    format_price,
    required_min_order_cents,
)

router = Router(name="cart")
log = logging.getLogger(__name__)


@router.callback_query(F.data == "cart:open")
async def show_cart(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        lang = user.language
        items = await repo.list_cart(session, user.id)
        total = repo.cart_total_cents(items)
        snapshot = [
            (i.id, i.product.name, i.quantity, i.product.price_cents) for i in items
        ]

    await call.answer()
    if not call.message:
        return
    if not snapshot:
        await call.message.answer(t("cart_empty", lang), reply_markup=main_menu_kb(lang))
        return

    lines = [t("cart_header", lang), ""]
    for _id, name, qty, price_cents in snapshot:
        lines.append(
            t(
                "cart_line",
                lang,
                name=name,
                qty=qty,
                line_total=format_price(price_cents * qty),
            )
        )
    lines.append("")
    lines.append(t("cart_total", lang, total=format_price(total)))
    await call.message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=cart_kb(lang, items),
    )


@router.callback_query(F.data.startswith("cart:del:"))
async def remove_cart_item(call: CallbackQuery, state: FSMContext) -> None:
    item_id = int(call.data.rsplit(":", 1)[1])
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        await repo.remove_cart_item(session, item_id, user.id)
    await call.answer()
    await show_cart(call, state)


# ---------- checkout ----------


@router.callback_query(F.data == "cart:checkout")
async def on_checkout_start(call: CallbackQuery, state: FSMContext) -> None:
    """Cart → ask delivery method."""
    await state.clear()
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        lang = user.language
        items = await repo.list_cart(session, user.id)
    if not items:
        await call.answer(t("cart_empty", lang), show_alert=True)
        return
    await call.answer()
    if call.message:
        await call.message.answer(
            t("checkout_choose_method", lang), reply_markup=checkout_method_kb(lang)
        )


@router.callback_query(F.data == "co:pickup")
async def on_checkout_pickup(
    call: CallbackQuery, state: FSMContext, config: Config
) -> None:
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        lang = user.language
    await call.answer()
    if call.message:
        await call.message.answer(
            t("pickup_choose_city", lang, city=config.pickup_city),
            reply_markup=checkout_pickup_city_kb(lang, config.pickup_city),
        )


@router.callback_query(F.data.startswith("co:city:"))
async def on_checkout_pickup_city(
    call: CallbackQuery, state: FSMContext, config: Config
) -> None:
    code = call.data.rsplit(":", 1)[1]
    pickup_city = config.pickup_city if code == "main" else "nearby"
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        lang = user.language
        items = await repo.list_cart(session, user.id)
        if not items:
            await call.answer(t("cart_empty", lang), show_alert=True)
            return
        total = repo.cart_total_cents(items)
        min_required = required_min_order_cents("pickup", pickup_city)
        if total < min_required:
            await call.answer()
            if call.message:
                await call.message.answer(
                    t("checkout_min_order", lang, total=format_price(total))
                )
            return
        order = await repo.create_order(
            session, user, delivery_method="pickup", pickup_city=pickup_city
        )

    await call.answer()
    if order is None:
        return
    if call.message:
        await call.message.answer(t("checkout_thanks", lang, order_id=order.id))
    await _notify_admins(call.bot, config, order)


@router.callback_query(F.data == "co:mail")
async def on_checkout_mail(call: CallbackQuery, state: FSMContext) -> None:
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        lang = user.language
    await state.set_state(Checkout.mail_address)
    await call.answer()
    if call.message:
        await call.message.answer(t("ask_address", lang))


@router.message(Checkout.mail_address, F.text)
async def on_mail_address(message: Message, state: FSMContext) -> None:
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, message.from_user.id, message.from_user.username
        )
        lang = user.language
    await state.update_data(address=message.text.strip())
    await state.set_state(Checkout.mail_recipient_name)
    await message.answer(t("ask_recipient_name", lang))


@router.message(Checkout.mail_recipient_name, F.text)
async def on_mail_recipient_name(message: Message, state: FSMContext) -> None:
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, message.from_user.id, message.from_user.username
        )
        lang = user.language
    await state.update_data(recipient_name=message.text.strip())
    await state.set_state(Checkout.mail_recipient_phone)
    await message.answer(t("ask_recipient_phone", lang))


@router.message(Checkout.mail_recipient_phone, F.text)
async def on_mail_recipient_phone(message: Message, state: FSMContext) -> None:
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, message.from_user.id, message.from_user.username
        )
        lang = user.language
    await state.update_data(recipient_phone=message.text.strip())
    await state.set_state(Checkout.mail_recipient_email)
    await message.answer(t("ask_recipient_email", lang))


def _looks_like_email(value: str) -> bool:
    if "@" not in value:
        return False
    local, _, domain = value.partition("@")
    return bool(local) and "." in domain and not domain.startswith(".")


@router.message(Checkout.mail_recipient_email, F.text)
async def on_mail_recipient_email(
    message: Message, state: FSMContext, config: Config
) -> None:
    email = message.text.strip()
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, message.from_user.id, message.from_user.username
        )
        lang = user.language
    if not _looks_like_email(email):
        await message.answer(t("invalid_email", lang))
        return
    data = await state.get_data()
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, message.from_user.id, message.from_user.username
        )
        items = await repo.list_cart(session, user.id)
        if not items:
            await state.clear()
            await message.answer(t("cart_empty", lang), reply_markup=main_menu_kb(lang))
            return
        order = await repo.create_order(
            session,
            user,
            delivery_method="mail",
            address=data.get("address", ""),
            recipient_name=data.get("recipient_name", ""),
            recipient_phone=data.get("recipient_phone", ""),
            recipient_email=email,
        )
    await state.clear()
    if order is None:
        return
    await message.answer(t("checkout_thanks", lang, order_id=order.id))
    await _notify_admins(message.bot, config, order)


async def _notify_admins(bot: Bot, config: Config, order) -> None:
    if not config.admin_ids:
        return
    text = format_order(order)
    for admin_id in config.admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            log.warning("Failed to notify admin %s: %s", admin_id, e)


__all__ = ["router", "PICKUP_MIN_ORDER_CENTS"]
