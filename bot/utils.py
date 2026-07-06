from __future__ import annotations

from .config import Config
from .db.models import Order, OrderItem
from .locales import t


def is_admin(config: Config, telegram_id: int) -> bool:
    return telegram_id in config.admin_ids


def format_price(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"


PICKUP_MIN_ORDER_CENTS = 4000


def required_min_order_cents(delivery_method: str | None, pickup_city: str | None) -> int:
    """Return min order in cents for the user's chosen delivery configuration."""
    if delivery_method == "pickup" and pickup_city == "nearby":
        return PICKUP_MIN_ORDER_CENTS
    return 0


def format_order(order: Order, *, lang: str = "en") -> str:
    """Format an order summary suitable for admin notifications.

    Always uses English-ish neutral labels regardless of the customer's language
    so admins always see a consistent message.
    """
    lines: list[str] = []
    lines.append(t("order_notification_header", lang, order_id=order.id))
    lines.append("")
    username = f"@{order.telegram_username}" if order.telegram_username else "—"
    lines.append(f"Customer: {username} (tg:{order.telegram_id})")
    lines.append(f"Language: {order.language}")
    if order.delivery_method == "pickup":
        city = order.pickup_city or "?"
        lines.append(f"Delivery: in-person pickup ({city})")
    elif order.delivery_method == "mail":
        lines.append("Delivery: mail")
        lines.append(f"Address: {order.address or '—'}")
        lines.append(f"Recipient: {order.recipient_name or '—'}")
        lines.append(f"Phone: {order.recipient_phone or '—'}")
        lines.append(f"Email: {order.recipient_email or '—'}")
    else:
        lines.append(f"Delivery: {order.delivery_method}")
    lines.append("")
    lines.append("Items:")
    for it in order.items:
        line_total = format_price(it.price_cents * it.quantity)
        unit = format_price(it.price_cents)
        lines.append(f"  • {it.product_name} ×{it.quantity} — €{line_total} (€{unit} each)")
    lines.append("")
    lines.append(f"Total: €{format_price(order.total_cents)}")
    return "\n".join(lines)


def format_order_short(order: Order) -> str:
    total = format_price(order.total_cents)
    username = f"@{order.telegram_username}" if order.telegram_username else "—"
    return f"#{order.id} · {username} · €{total} · {order.delivery_method}"


__all__ = [
    "PICKUP_MIN_ORDER_CENTS",
    "format_order",
    "format_order_short",
    "format_price",
    "is_admin",
    "required_min_order_cents",
]
