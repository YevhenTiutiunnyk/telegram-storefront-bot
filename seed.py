"""Populate the database with a small, fictional coffee & tea catalog.

Run once after setting up your `.env`:

    python seed.py

Safe to re-run: if any brands already exist it does nothing (pass --force to
seed anyway). No real customers or orders are created — catalog data only.
"""

from __future__ import annotations

import asyncio
import os
import sys

from dotenv import load_dotenv

from bot.db import base, repo

load_dotenv()

# (brand, category, brand_description, [(line, line_description, [(product, price_eur, description)])])
CATALOG = [
    (
        "Blue Barrel Roasters",
        "coffee",
        "Small-batch specialty roaster.",
        [
            (
                "Bella Donovan",
                "A chocolatey, full-bodied everyday blend.",
                [
                    ("Whole bean 250g", 14.00, "Our house blend, roasted weekly."),
                    ("Whole bean 1kg", 48.00, "Same blend, better value."),
                    ("Ground for filter 250g", 14.00, "Medium grind for pour-over."),
                ],
            ),
            (
                "Morning Ritual",
                "Bright and balanced single-origin.",
                [
                    ("Whole bean 250g", 13.50, "Notes of citrus and honey."),
                    ("Drip bags ×10", 9.00, "One cup, anywhere."),
                ],
            ),
        ],
    ),
    (
        "Northern Fog Coffee",
        "coffee",
        "Direct-trade micro-lots.",
        [
            (
                "Ethiopia Yirgacheffe",
                "Floral and tea-like.",
                [
                    ("Whole bean 250g", 16.00, "Washed process, light roast."),
                ],
            ),
        ],
    ),
    (
        "Rare Leaf Tea Co",
        "tea",
        "Loose-leaf teas sourced from small gardens.",
        [
            (
                "Sencha Green",
                "Grassy Japanese green tea.",
                [
                    ("Loose leaf 100g", 11.00, "First-flush sencha."),
                    ("Sachets ×15", 7.50, "Whole-leaf pyramid bags."),
                ],
            ),
            (
                "Earl Grey Supreme",
                "Black tea with bergamot and cornflower.",
                [
                    ("Loose leaf 100g", 10.00, "A classic, done well."),
                ],
            ),
        ],
    ),
    (
        "Kettle & Co",
        "equipment",
        "Brewing gear for home baristas.",
        [
            (
                "Pour-Over Set",
                "Everything for a clean filter cup.",
                [
                    ("Ceramic dripper", 18.00, "Size 02, fits most servers."),
                    ("Glass server 600ml", 22.00, "Heatproof borosilicate."),
                ],
            ),
            (
                "GrindWell Hand Grinder",
                "Consistent grind, quietly.",
                [
                    ("Compact hand grinder", 39.00, "Stainless burrs, 25g capacity."),
                ],
            ),
        ],
    ),
    (
        "Daily Brew",
        "accessories",
        "The little things that make the ritual.",
        [
            (
                "Mugs",
                "Drink it in style.",
                [
                    ("Ceramic mug 350ml", 12.00, "Matte glaze, dishwasher safe."),
                    ("Travel tumbler", 19.00, "Leak-proof, keeps heat 4h."),
                ],
            ),
            (
                "Filters",
                "Consumables and refills.",
                [
                    ("Paper filters ×100", 6.00, "Size 02, unbleached."),
                ],
            ),
        ],
    ),
]


async def seed(force: bool = False) -> None:
    db_path = os.getenv("DB_PATH", "bot.db").strip() or "bot.db"
    await base.init_db(db_path)

    async with repo.db_session() as session:
        existing = await repo.list_brands(session)
    if existing and not force:
        print(
            f"{len(existing)} brand(s) already present in {db_path}; nothing to do. "
            "Pass --force to seed anyway."
        )
        return

    created = 0
    for brand_name, category, brand_desc, lines in CATALOG:
        async with repo.db_session() as session:
            brand = await repo.create_brand(session, brand_name, category, brand_desc)
            for line_name, line_desc, products in lines:
                model = await repo.create_model(session, brand.id, line_name, None, line_desc)
                for product_name, price_eur, product_desc in products:
                    await repo.create_product(
                        session,
                        model_id=model.id,
                        name=product_name,
                        description=product_desc,
                        price_cents=round(price_eur * 100),
                        photo_file_id=None,
                    )
                    created += 1
    print(f"Seeded {created} products across {len(CATALOG)} brands into {db_path}.")


if __name__ == "__main__":
    asyncio.run(seed(force="--force" in sys.argv))
