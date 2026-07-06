from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .base import session_factory
from .models import (
    Brand,
    CartItem,
    Model,
    Order,
    OrderItem,
    Product,
    User,
)


@asynccontextmanager
async def db_session() -> AsyncIterator[AsyncSession]:
    async with session_factory()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------- users ----------


async def get_or_create_user(
    session: AsyncSession, telegram_id: int, username: str | None
) -> User:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id, username=username, language="en")
        session.add(user)
        await session.flush()
    elif username and user.username != username:
        user.username = username
    return user


async def get_user_by_telegram_id(
    session: AsyncSession, telegram_id: int
) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def set_language(session: AsyncSession, user_id: int, lang: str) -> None:
    user = await session.get(User, user_id)
    if user:
        user.language = lang


# ---------- catalog (read) ----------


async def list_brands(session: AsyncSession, category: str | None = None) -> list[Brand]:
    stmt = select(Brand)
    if category is not None:
        stmt = stmt.where(Brand.category == category)
    result = await session.execute(stmt.order_by(Brand.name))
    return list(result.scalars().all())


async def list_models(session: AsyncSession, brand_id: int) -> list[Model]:
    result = await session.execute(
        select(Model).where(Model.brand_id == brand_id).order_by(Model.name)
    )
    return list(result.scalars().all())


async def list_products(session: AsyncSession, model_id: int) -> list[Product]:
    result = await session.execute(
        select(Product).where(Product.model_id == model_id).order_by(Product.name)
    )
    return list(result.scalars().all())


async def get_brand(session: AsyncSession, brand_id: int) -> Brand | None:
    return await session.get(Brand, brand_id)


async def get_model(session: AsyncSession, model_id: int) -> Model | None:
    return await session.get(Model, model_id)


async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    return await session.get(Product, product_id)


# ---------- catalog (write) ----------


async def create_brand(
    session: AsyncSession,
    name: str,
    category: str,
    description: str | None = None,
) -> Brand:
    brand = Brand(name=name, category=category, description=description)
    session.add(brand)
    await session.flush()
    return brand


async def create_model(
    session: AsyncSession,
    brand_id: int,
    name: str,
    photo_file_id: str | None,
    description: str | None = None,
) -> Model:
    model = Model(
        brand_id=brand_id,
        name=name,
        photo_file_id=photo_file_id,
        description=description,
    )
    session.add(model)
    await session.flush()
    return model


async def create_product(
    session: AsyncSession,
    model_id: int,
    name: str,
    description: str | None,
    price_cents: int,
    photo_file_id: str | None,
) -> Product:
    product = Product(
        model_id=model_id,
        name=name,
        description=description,
        price_cents=price_cents,
        photo_file_id=photo_file_id,
    )
    session.add(product)
    await session.flush()
    return product


async def update_brand(
    session: AsyncSession,
    brand_id: int,
    name: str | None = None,
    description: str | None = None,
) -> None:
    brand = await session.get(Brand, brand_id)
    if not brand:
        return
    if name is not None:
        brand.name = name
    if description is not None:
        brand.description = description


async def update_model(
    session: AsyncSession,
    model_id: int,
    name: str | None = None,
    photo_file_id: str | None = None,
    description: str | None = None,
) -> None:
    model = await session.get(Model, model_id)
    if not model:
        return
    if name is not None:
        model.name = name
    if photo_file_id is not None:
        model.photo_file_id = photo_file_id
    if description is not None:
        model.description = description


async def update_product(
    session: AsyncSession,
    product_id: int,
    name: str | None = None,
    description: str | None = None,
    price_cents: int | None = None,
    photo_file_id: str | None = None,
) -> None:
    product = await session.get(Product, product_id)
    if not product:
        return
    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if price_cents is not None:
        product.price_cents = price_cents
    if photo_file_id is not None:
        product.photo_file_id = photo_file_id


async def delete_brand(session: AsyncSession, brand_id: int) -> None:
    brand = await session.get(Brand, brand_id)
    if brand:
        await session.delete(brand)


async def delete_model(session: AsyncSession, model_id: int) -> None:
    model = await session.get(Model, model_id)
    if model:
        await session.delete(model)


async def delete_product(session: AsyncSession, product_id: int) -> None:
    product = await session.get(Product, product_id)
    if product:
        await session.delete(product)


# ---------- cart ----------


async def add_to_cart(
    session: AsyncSession, user_id: int, product_id: int, quantity: int
) -> None:
    result = await session.execute(
        select(CartItem).where(
            CartItem.user_id == user_id, CartItem.product_id == product_id
        )
    )
    item = result.scalar_one_or_none()
    if item is None:
        session.add(
            CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        )
    else:
        item.quantity += quantity


async def list_cart(session: AsyncSession, user_id: int) -> list[CartItem]:
    result = await session.execute(
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .options(selectinload(CartItem.product))
        .order_by(CartItem.id)
    )
    return list(result.scalars().all())


async def remove_cart_item(session: AsyncSession, item_id: int, user_id: int) -> None:
    await session.execute(
        delete(CartItem).where(CartItem.id == item_id, CartItem.user_id == user_id)
    )


async def clear_cart(session: AsyncSession, user_id: int) -> None:
    await session.execute(delete(CartItem).where(CartItem.user_id == user_id))


def cart_total_cents(items: list[CartItem]) -> int:
    return sum(i.product.price_cents * i.quantity for i in items)


# ---------- orders ----------


async def create_order(
    session: AsyncSession,
    user: User,
    *,
    delivery_method: str,
    pickup_city: str | None = None,
    address: str | None = None,
    recipient_name: str | None = None,
    recipient_phone: str | None = None,
    recipient_email: str | None = None,
) -> Order | None:
    items = await list_cart(session, user.id)
    if not items:
        return None
    total = cart_total_cents(items)
    order = Order(
        user_id=user.id,
        telegram_id=user.telegram_id,
        telegram_username=user.username,
        language=user.language,
        delivery_method=delivery_method,
        pickup_city=pickup_city,
        address=address,
        recipient_name=recipient_name,
        recipient_phone=recipient_phone,
        recipient_email=recipient_email,
        total_cents=total,
    )
    session.add(order)
    await session.flush()
    for item in items:
        session.add(
            OrderItem(
                order_id=order.id,
                product_name=item.product.name,
                quantity=item.quantity,
                price_cents=item.product.price_cents,
            )
        )
    await session.execute(delete(CartItem).where(CartItem.user_id == user.id))
    await session.flush()
    # Eagerly load items so they're accessible after commit
    await session.refresh(order, attribute_names=["items"])
    return order


async def recent_orders(session: AsyncSession, limit: int = 20) -> list[Order]:
    result = await session.execute(
        select(Order)
        .options(selectinload(Order.items))
        .order_by(desc(Order.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_order(session: AsyncSession, order_id: int) -> Order | None:
    result = await session.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    )
    return result.scalar_one_or_none()
