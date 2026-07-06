from aiogram import Dispatcher

from . import admin, cart, catalog, start


def register_routers(dp: Dispatcher) -> None:
    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(cart.router)
    dp.include_router(admin.router)
