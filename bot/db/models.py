from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64))
    language: Mapped[str] = mapped_column(String(4), default="en")

    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


# Storefront categories, in display order.
CATEGORIES: tuple[str, ...] = ("coffee", "tea", "equipment", "accessories")


class Brand(Base):
    __tablename__ = "brands"
    __table_args__ = (UniqueConstraint("name", "category", name="uq_brand_name_category"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(
        String(16), default="coffee", server_default="coffee"
    )
    description: Mapped[str | None] = mapped_column(String(1024))

    models: Mapped[list["Model"]] = relationship(
        back_populates="brand", cascade="all, delete-orphan"
    )


class Model(Base):
    """A product line within a brand (e.g. a specific blend or roast)."""

    __tablename__ = "models"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(String(1024))
    photo_file_id: Mapped[str | None] = mapped_column(String(256))

    brand: Mapped[Brand] = relationship(back_populates="models")
    products: Mapped[list["Product"]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )


class Product(Base):
    """A sellable item — a concrete SKU with a price."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("models.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(String(1024))
    price_cents: Mapped[int] = mapped_column(Integer)
    photo_file_id: Mapped[str | None] = mapped_column(String(256))

    model: Mapped[Model] = relationship(back_populates="products")


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_cart_user_product"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    user: Mapped[User] = relationship(back_populates="cart_items")
    product: Mapped[Product] = relationship()


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    telegram_id: Mapped[int] = mapped_column(BigInteger)
    telegram_username: Mapped[str | None] = mapped_column(String(64))
    language: Mapped[str] = mapped_column(String(4), default="en")
    delivery_method: Mapped[str] = mapped_column(String(16))
    pickup_city: Mapped[str | None] = mapped_column(String(32))
    address: Mapped[str | None] = mapped_column(String(512))
    recipient_name: Mapped[str | None] = mapped_column(String(128))
    recipient_phone: Mapped[str | None] = mapped_column(String(64))
    recipient_email: Mapped[str | None] = mapped_column(String(256))
    total_cents: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    """A line item stored as a snapshot of name + price at order time, so order
    history survives later catalog edits."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_name: Mapped[str] = mapped_column(String(256))
    quantity: Mapped[int] = mapped_column(Integer)
    price_cents: Mapped[int] = mapped_column(Integer)

    order: Mapped[Order] = relationship(back_populates="items")
