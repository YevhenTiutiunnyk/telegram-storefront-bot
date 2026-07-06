from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..db import repo
from ..keyboards import language_kb, main_menu_kb
from ..locales import LANGS, t

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    async with repo.db_session() as session:
        existing = await repo.get_user_by_telegram_id(session, message.from_user.id)
        user = await repo.get_or_create_user(
            session, message.from_user.id, message.from_user.username
        )
        lang = user.language

    if existing is None:
        await message.answer(t("choose_language", lang), reply_markup=language_kb())
        return
    await message.answer(t("menu_prompt", lang), reply_markup=main_menu_kb(lang))


@router.message(Command("language"))
async def cmd_language(message: Message) -> None:
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, message.from_user.id, message.from_user.username
        )
        lang = user.language
    await message.answer(t("choose_language", lang), reply_markup=language_kb())


@router.callback_query(F.data.startswith("lang:"))
async def on_language(call: CallbackQuery, state: FSMContext) -> None:
    code = call.data.split(":", 1)[1]
    if code not in LANGS:
        await call.answer()
        return
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        await repo.set_language(session, user.id, code)

    await call.answer(t("language_set", code))
    if call.message:
        await call.message.edit_text(t("language_set", code))
        await call.message.answer(t("menu_prompt", code), reply_markup=main_menu_kb(code))


@router.callback_query(F.data == "cfg:lang")
async def on_change_language(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        lang = user.language
    await call.answer()
    if call.message:
        await call.message.answer(t("choose_language", lang), reply_markup=language_kb())


@router.callback_query(F.data == "menu:home")
async def on_menu_home(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    async with repo.db_session() as session:
        user = await repo.get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        lang = user.language
    await call.answer()
    if call.message:
        await call.message.answer(t("menu_prompt", lang), reply_markup=main_menu_kb(lang))
