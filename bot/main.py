from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .config import load_config
from .db.base import init_db
from .handlers import register_routers


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    config = load_config()
    await init_db(config.db_path)

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    register_routers(dp)

    logging.info("Bot starting; admin_ids=%s", sorted(config.admin_ids))
    try:
        await dp.start_polling(bot, config=config)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
