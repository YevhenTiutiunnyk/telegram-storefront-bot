"""Translations for all user-facing strings.

`t(key, lang, **kwargs)` returns the string for the requested language, falling
back to English if the key is missing or the language is unknown.
"""

from __future__ import annotations

LANGS: tuple[str, ...] = ("en", "ru", "uk", "nl")

LANG_NAMES: dict[str, str] = {
    "en": "English",
    "ru": "Русский",
    "uk": "Українська",
    "nl": "Nederlands",
}


STRINGS: dict[str, dict[str, str]] = {
    # ---------- onboarding ----------
    "choose_language": {
        "en": "Please choose your language:",
        "ru": "Пожалуйста, выберите язык:",
        "uk": "Будь ласка, оберіть мову:",
        "nl": "Kies je taal:",
    },
    "language_set": {
        "en": "Language set to English.",
        "ru": "Язык установлен: Русский.",
        "uk": "Мову встановлено: Українська.",
        "nl": "Taal ingesteld op Nederlands.",
    },
    "checkout_choose_method": {
        "en": "How would you like to receive your order?",
        "ru": "Как вы хотите получить заказ?",
        "uk": "Як ви хочете отримати замовлення?",
        "nl": "Hoe wil je je bestelling ontvangen?",
    },
    "delivery_mail": {
        "en": "📦 Mail delivery",
        "ru": "📦 Доставка почтой",
        "uk": "📦 Доставка поштою",
        "nl": "📦 Verzending per post",
    },
    "delivery_pickup": {
        "en": "🤝 In-person pickup",
        "ru": "🤝 Личная встреча",
        "uk": "🤝 Особиста зустріч",
        "nl": "🤝 Persoonlijk afhalen",
    },
    "pickup_choose_city": {
        "en": "In-person pickup is available in {city} and nearby towns. Nearby towns have a €40 minimum order.",
        "ru": "Самовывоз доступен в {city} и близлежащих городах. В близлежащих городах минимальный заказ €40.",
        "uk": "Самовивіз доступний у {city} та найближчих містах. У сусідніх містах мінімальне замовлення €40.",
        "nl": "Afhalen is mogelijk in {city} en nabijgelegen plaatsen. Nabijgelegen plaatsen hebben een minimum bestelling van €40.",
    },
    "pickup_city_main": {
        "en": "{city}",
        "ru": "{city}",
        "uk": "{city}",
        "nl": "{city}",
    },
    "pickup_city_nearby": {
        "en": "Nearby town (min. €40)",
        "ru": "Близлежащий город (мин. €40)",
        "uk": "Сусіднє місто (мін. €40)",
        "nl": "Nabijgelegen plaats (min. €40)",
    },
    "ask_address": {
        "en": "Please send your delivery address (street, house, postcode, city, country):",
        "ru": "Пожалуйста, отправьте адрес доставки (улица, дом, индекс, город, страна):",
        "uk": "Будь ласка, надішліть адресу доставки (вулиця, будинок, індекс, місто, країна):",
        "nl": "Stuur je bezorgadres (straat, huisnummer, postcode, plaats, land):",
    },
    "ask_recipient_name": {
        "en": "Recipient's full name:",
        "ru": "Полное имя получателя:",
        "uk": "Повне ім'я отримувача:",
        "nl": "Volledige naam van de ontvanger:",
    },
    "ask_recipient_phone": {
        "en": "Recipient's phone number:",
        "ru": "Номер телефона получателя:",
        "uk": "Номер телефону отримувача:",
        "nl": "Telefoonnummer van de ontvanger:",
    },
    "ask_recipient_email": {
        "en": "Recipient's email:",
        "ru": "Email получателя:",
        "uk": "Email отримувача:",
        "nl": "E-mailadres van de ontvanger:",
    },
    "invalid_email": {
        "en": "That doesn't look like a valid email. Try again:",
        "ru": "Это не похоже на email. Попробуйте ещё раз:",
        "uk": "Це не схоже на email. Спробуйте ще раз:",
        "nl": "Dat lijkt geen geldig e-mailadres. Probeer opnieuw:",
    },
    "delivery_saved": {
        "en": "Thanks! Your delivery preferences are saved.",
        "ru": "Спасибо! Ваши настройки доставки сохранены.",
        "uk": "Дякуємо! Ваші налаштування доставки збережено.",
        "nl": "Bedankt! Je bezorginstellingen zijn opgeslagen.",
    },
    # ---------- main menu ----------
    "menu_catalog": {
        "en": "🛍 Catalog",
        "ru": "🛍 Каталог",
        "uk": "🛍 Каталог",
        "nl": "🛍 Catalogus",
    },
    "menu_cart": {
        "en": "🧺 Cart",
        "ru": "🧺 Корзина",
        "uk": "🧺 Кошик",
        "nl": "🧺 Winkelmandje",
    },
    "menu_change_language": {
        "en": "⚙️ Change language",
        "ru": "⚙️ Сменить язык",
        "uk": "⚙️ Змінити мову",
        "nl": "⚙️ Taal wijzigen",
    },
    "support": {
        "en": "🆘 Support",
        "ru": "🆘 Поддержка",
        "uk": "🆘 Підтримка",
        "nl": "🆘 Hulp",
    },
    "menu_prompt": {
        "en": "Choose an option:",
        "ru": "Выберите опцию:",
        "uk": "Оберіть опцію:",
        "nl": "Kies een optie:",
    },
    # ---------- catalog ----------
    "no_brands": {
        "en": "The catalog is empty right now. Please check back later.",
        "ru": "Каталог пока пуст. Загляните позже.",
        "uk": "Каталог поки що порожній. Завітайте пізніше.",
        "nl": "De catalogus is op dit moment leeg. Kom later terug.",
    },
    "no_models": {
        "en": "No product lines for this brand yet.",
        "ru": "Для этого бренда пока нет линеек.",
        "uk": "Для цього бренду поки немає лінійок.",
        "nl": "Nog geen productlijnen voor dit merk.",
    },
    "no_products": {
        "en": "No products in this line yet.",
        "ru": "В этой линейке пока нет товаров.",
        "uk": "У цій лінійці поки немає товарів.",
        "nl": "Nog geen producten in deze lijn.",
    },
    "brands_title": {
        "en": "Catalog",
        "ru": "Каталог",
        "uk": "Каталог",
        "nl": "Catalogus",
    },
    "models_title": {
        "en": "{brand} — product lines:",
        "ru": "{brand} — линейки:",
        "uk": "{brand} — лінійки:",
        "nl": "{brand} — productlijnen:",
    },
    "products_title": {
        "en": "Products in {model}:",
        "ru": "Товары в {model}:",
        "uk": "Товари у {model}:",
        "nl": "Producten in {model}:",
    },
    "back": {"en": "« Back", "ru": "« Назад", "uk": "« Назад", "nl": "« Terug"},
    "back_to_brands": {
        "en": "« Brands",
        "ru": "« Бренды",
        "uk": "« Бренди",
        "nl": "« Merken",
    },
    "back_to_models": {
        "en": "« Product lines",
        "ru": "« Линейки",
        "uk": "« Лінійки",
        "nl": "« Productlijnen",
    },
    "back_to_menu": {
        "en": "« Menu",
        "ru": "« Меню",
        "uk": "« Меню",
        "nl": "« Menu",
    },
    "choose_category": {
        "en": "Choose a category:",
        "ru": "Выберите категорию:",
        "uk": "Оберіть категорію:",
        "nl": "Kies een categorie:",
    },
    "no_brands_in_category": {
        "en": "No brands in this category yet.",
        "ru": "В этой категории пока нет брендов.",
        "uk": "У цій категорії поки немає брендів.",
        "nl": "Nog geen merken in deze categorie.",
    },
    "back_to_categories": {
        "en": "« Categories",
        "ru": "« Категории",
        "uk": "« Категорії",
        "nl": "« Categorieën",
    },
    "cat_coffee": {
        "en": "☕ Coffee",
        "ru": "☕ Кофе",
        "uk": "☕ Кава",
        "nl": "☕ Koffie",
    },
    "cat_tea": {
        "en": "🍵 Tea",
        "ru": "🍵 Чай",
        "uk": "🍵 Чай",
        "nl": "🍵 Thee",
    },
    "cat_equipment": {
        "en": "🫖 Equipment",
        "ru": "🫖 Оборудование",
        "uk": "🫖 Обладнання",
        "nl": "🫖 Apparatuur",
    },
    "cat_accessories": {
        "en": "🥄 Accessories",
        "ru": "🥄 Аксессуары",
        "uk": "🥄 Аксесуари",
        "nl": "🥄 Accessoires",
    },
    "product_caption": {
        "en": "<b>{name}</b>\nPrice: €{price}\n\n{description}",
        "ru": "<b>{name}</b>\nЦена: €{price}\n\n{description}",
        "uk": "<b>{name}</b>\nЦіна: €{price}\n\n{description}",
        "nl": "<b>{name}</b>\nPrijs: €{price}\n\n{description}",
    },
    "qty_label": {
        "en": "Quantity: {qty}",
        "ru": "Количество: {qty}",
        "uk": "Кількість: {qty}",
        "nl": "Aantal: {qty}",
    },
    "add_to_cart": {
        "en": "➕ Add to cart",
        "ru": "➕ В корзину",
        "uk": "➕ До кошика",
        "nl": "➕ Toevoegen",
    },
    "added_to_cart": {
        "en": "Added to cart: {name} ×{qty}",
        "ru": "Добавлено в корзину: {name} ×{qty}",
        "uk": "Додано до кошика: {name} ×{qty}",
        "nl": "Toegevoegd: {name} ×{qty}",
    },
    # ---------- cart ----------
    "cart_empty": {
        "en": "Your cart is empty.",
        "ru": "Корзина пуста.",
        "uk": "Ваш кошик порожній.",
        "nl": "Je winkelmandje is leeg.",
    },
    "cart_header": {
        "en": "<b>Your cart</b>",
        "ru": "<b>Ваша корзина</b>",
        "uk": "<b>Ваш кошик</b>",
        "nl": "<b>Je winkelmandje</b>",
    },
    "cart_line": {
        "en": "• {name} ×{qty} — €{line_total}",
        "ru": "• {name} ×{qty} — €{line_total}",
        "uk": "• {name} ×{qty} — €{line_total}",
        "nl": "• {name} ×{qty} — €{line_total}",
    },
    "cart_total": {
        "en": "Total: <b>€{total}</b>",
        "ru": "Итого: <b>€{total}</b>",
        "uk": "Разом: <b>€{total}</b>",
        "nl": "Totaal: <b>€{total}</b>",
    },
    "cart_remove": {
        "en": "🗑 Remove {name}",
        "ru": "🗑 Удалить {name}",
        "uk": "🗑 Видалити {name}",
        "nl": "🗑 Verwijder {name}",
    },
    "cart_checkout": {
        "en": "✅ Checkout",
        "ru": "✅ Оформить заказ",
        "uk": "✅ Оформити замовлення",
        "nl": "✅ Afrekenen",
    },
    "checkout_min_order": {
        "en": "Minimum order for nearby-town pickup is €40. Your total is €{total}. Please add more items.",
        "ru": "Минимальный заказ для самовывоза в близлежащих городах — €40. Ваша сумма €{total}. Добавьте ещё товары.",
        "uk": "Мінімальне замовлення для самовивозу в сусідніх містах — €40. Ваша сума €{total}. Додайте більше товарів.",
        "nl": "Minimum bestelling voor afhalen in nabijgelegen plaatsen is €40. Je totaal is €{total}. Voeg meer producten toe.",
    },
    "checkout_no_delivery": {
        "en": "Please set up your delivery preferences first.",
        "ru": "Сначала настройте способ доставки.",
        "uk": "Спочатку налаштуйте спосіб доставки.",
        "nl": "Stel eerst je bezorgvoorkeuren in.",
    },
    "checkout_thanks": {
        "en": "Thank you for your order! Order #{order_id}. We'll be in touch soon.",
        "ru": "Спасибо за заказ! Заказ №{order_id}. Мы скоро свяжемся с вами.",
        "uk": "Дякуємо за замовлення! Замовлення №{order_id}. Ми скоро з вами зв'яжемося.",
        "nl": "Bedankt voor je bestelling! Bestelling #{order_id}. We nemen snel contact op.",
    },
    # ---------- admin ----------
    "admin_only": {
        "en": "Admins only.",
        "ru": "Только для администраторов.",
        "uk": "Лише для адміністраторів.",
        "nl": "Alleen voor beheerders.",
    },
    "admin_menu": {
        "en": "Admin panel:",
        "ru": "Админ-панель:",
        "uk": "Адмін-панель:",
        "nl": "Beheerpaneel:",
    },
    "admin_view_catalog": {
        "en": "📚 View catalog",
        "ru": "📚 Каталог",
        "uk": "📚 Каталог",
        "nl": "📚 Catalogus",
    },
    "admin_add_product": {
        "en": "➕ Add product",
        "ru": "➕ Добавить товар",
        "uk": "➕ Додати товар",
        "nl": "➕ Product toevoegen",
    },
    "admin_recent_orders": {
        "en": "🧾 Recent orders",
        "ru": "🧾 Последние заказы",
        "uk": "🧾 Останні замовлення",
        "nl": "🧾 Recente bestellingen",
    },
    "admin_edit": {"en": "✏️ Edit", "ru": "✏️ Изм.", "uk": "✏️ Ред.", "nl": "✏️ Bewerken"},
    "admin_delete": {
        "en": "🗑 Delete",
        "ru": "🗑 Удалить",
        "uk": "🗑 Видалити",
        "nl": "🗑 Verwijderen",
    },
    "admin_confirm_delete": {
        "en": "Delete {name}? This will cascade to its children.",
        "ru": "Удалить {name}? Все вложенные элементы тоже будут удалены.",
        "uk": "Видалити {name}? Усі вкладені елементи також буде видалено.",
        "nl": "{name} verwijderen? Onderliggende items worden ook verwijderd.",
    },
    "admin_confirm_yes": {
        "en": "Yes, delete",
        "ru": "Да, удалить",
        "uk": "Так, видалити",
        "nl": "Ja, verwijder",
    },
    "admin_confirm_no": {
        "en": "Cancel",
        "ru": "Отмена",
        "uk": "Скасувати",
        "nl": "Annuleren",
    },
    "admin_deleted": {
        "en": "Deleted.",
        "ru": "Удалено.",
        "uk": "Видалено.",
        "nl": "Verwijderd.",
    },
    "admin_add_pick_brand": {
        "en": "Pick a brand or create a new one:",
        "ru": "Выберите бренд или создайте новый:",
        "uk": "Оберіть бренд або створіть новий:",
        "nl": "Kies een merk of maak een nieuw merk aan:",
    },
    "admin_add_pick_model": {
        "en": "Pick a product line or create a new one:",
        "ru": "Выберите линейку или создайте новую:",
        "uk": "Оберіть лінійку або створіть нову:",
        "nl": "Kies een productlijn of maak een nieuwe aan:",
    },
    "admin_new_brand": {
        "en": "➕ New brand",
        "ru": "➕ Новый бренд",
        "uk": "➕ Новий бренд",
        "nl": "➕ Nieuw merk",
    },
    "admin_new_model": {
        "en": "➕ New product line",
        "ru": "➕ Новая линейка",
        "uk": "➕ Нова лінійка",
        "nl": "➕ Nieuwe productlijn",
    },
    "admin_ask_brand_name": {
        "en": "Send the brand name:",
        "ru": "Отправьте название бренда:",
        "uk": "Надішліть назву бренду:",
        "nl": "Stuur de merknaam:",
    },
    "admin_ask_model_name": {
        "en": "Send the product line name:",
        "ru": "Отправьте название линейки:",
        "uk": "Надішліть назву лінійки:",
        "nl": "Stuur de naam van de productlijn:",
    },
    "admin_ask_model_photo": {
        "en": "Send a photo for this product line (or send /skip):",
        "ru": "Отправьте фото линейки (или /skip, чтобы пропустить):",
        "uk": "Надішліть фото лінійки (або /skip, щоб пропустити):",
        "nl": "Stuur een foto voor deze productlijn (of /skip):",
    },
    "admin_ask_product_name": {
        "en": "Send the product name:",
        "ru": "Отправьте название товара:",
        "uk": "Надішліть назву товару:",
        "nl": "Stuur de productnaam:",
    },
    "admin_ask_product_price": {
        "en": "Send the price in EUR (e.g. 24.50):",
        "ru": "Отправьте цену в EUR (например, 24.50):",
        "uk": "Надішліть ціну в EUR (наприклад, 24.50):",
        "nl": "Stuur de prijs in EUR (bijv. 24.50):",
    },
    "admin_ask_product_description": {
        "en": "Send a short description (or /skip):",
        "ru": "Отправьте краткое описание (или /skip):",
        "uk": "Надішліть короткий опис (або /skip):",
        "nl": "Stuur een korte beschrijving (of /skip):",
    },
    "admin_ask_brand_description": {
        "en": "Send a description for this brand (or /skip):",
        "ru": "Отправьте описание бренда (или /skip):",
        "uk": "Надішліть опис бренду (або /skip):",
        "nl": "Stuur een beschrijving voor dit merk (of /skip):",
    },
    "admin_ask_model_description": {
        "en": "Send a description for this product line (or /skip):",
        "ru": "Отправьте описание линейки (или /skip):",
        "uk": "Надішліть опис лінійки (або /skip):",
        "nl": "Stuur een beschrijving voor deze productlijn (of /skip):",
    },
    "admin_ask_product_photo": {
        "en": "Send a product photo (or /skip):",
        "ru": "Отправьте фото товара (или /skip):",
        "uk": "Надішліть фото товару (або /skip):",
        "nl": "Stuur een productfoto (of /skip):",
    },
    "admin_invalid_price": {
        "en": "That doesn't look like a valid price. Try again (e.g. 24.50):",
        "ru": "Это не похоже на цену. Попробуйте снова (например, 24.50):",
        "uk": "Це не схоже на ціну. Спробуйте ще раз (наприклад, 24.50):",
        "nl": "Dat lijkt geen geldige prijs. Probeer opnieuw (bijv. 24.50):",
    },
    "admin_send_photo_or_skip": {
        "en": "Please send a photo or /skip.",
        "ru": "Пожалуйста, отправьте фото или /skip.",
        "uk": "Будь ласка, надішліть фото або /skip.",
        "nl": "Stuur een foto of /skip.",
    },
    "admin_product_added": {
        "en": "✅ Added: {name} (€{price}) under {brand} / {model}.",
        "ru": "✅ Добавлено: {name} (€{price}) — {brand} / {model}.",
        "uk": "✅ Додано: {name} (€{price}) — {brand} / {model}.",
        "nl": "✅ Toegevoegd: {name} (€{price}) onder {brand} / {model}.",
    },
    "admin_edit_field": {
        "en": "What do you want to edit?",
        "ru": "Что вы хотите изменить?",
        "uk": "Що ви хочете змінити?",
        "nl": "Wat wil je bewerken?",
    },
    "admin_edit_name": {"en": "Name", "ru": "Название", "uk": "Назва", "nl": "Naam"},
    "admin_edit_price": {"en": "Price", "ru": "Цена", "uk": "Ціна", "nl": "Prijs"},
    "admin_edit_description": {
        "en": "Description",
        "ru": "Описание",
        "uk": "Опис",
        "nl": "Beschrijving",
    },
    "admin_edit_photo": {"en": "Photo", "ru": "Фото", "uk": "Фото", "nl": "Foto"},
    "admin_send_new_value": {
        "en": "Send the new value:",
        "ru": "Отправьте новое значение:",
        "uk": "Надішліть нове значення:",
        "nl": "Stuur de nieuwe waarde:",
    },
    "admin_updated": {
        "en": "✅ Updated.",
        "ru": "✅ Обновлено.",
        "uk": "✅ Оновлено.",
        "nl": "✅ Bijgewerkt.",
    },
    "admin_no_orders": {
        "en": "No orders yet.",
        "ru": "Заказов пока нет.",
        "uk": "Замовлень поки немає.",
        "nl": "Nog geen bestellingen.",
    },
    "admin_orders_header": {
        "en": "Last {n} orders:",
        "ru": "Последние {n} заказов:",
        "uk": "Останні {n} замовлень:",
        "nl": "Laatste {n} bestellingen:",
    },
    "cancel": {"en": "Cancel", "ru": "Отмена", "uk": "Скасувати", "nl": "Annuleren"},
    "cancelled": {
        "en": "Cancelled.",
        "ru": "Отменено.",
        "uk": "Скасовано.",
        "nl": "Geannuleerd.",
    },
    # ---------- admin notification ----------
    "order_notification_header": {
        "en": "🔔 New order #{order_id}",
        "ru": "🔔 Новый заказ №{order_id}",
        "uk": "🔔 Нове замовлення №{order_id}",
        "nl": "🔔 Nieuwe bestelling #{order_id}",
    },
}


def t(key: str, lang: str = "en", **kwargs: object) -> str:
    """Translate `key` to `lang`, falling back to English on missing data."""
    entry = STRINGS.get(key)
    if entry is None:
        return key
    template = entry.get(lang) or entry.get("en") or key
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template
