import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_ids: frozenset[int]
    db_path: str
    support_username: str
    pickup_city: str


def _parse_admin_ids(raw: str) -> frozenset[int]:
    ids: set[int] = set()
    for piece in raw.split(","):
        piece = piece.strip()
        if not piece:
            continue
        try:
            ids.add(int(piece))
        except ValueError:
            raise ValueError(f"ADMIN_IDS contains non-integer value: {piece!r}")
    return frozenset(ids)


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is not set")
    return Config(
        bot_token=token,
        admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS", "")),
        db_path=os.getenv("DB_PATH", "bot.db").strip() or "bot.db",
        support_username=os.getenv("SUPPORT_USERNAME", "demo_support").strip().lstrip("@")
        or "demo_support",
        pickup_city=os.getenv("PICKUP_CITY", "Amsterdam").strip() or "Amsterdam",
    )
