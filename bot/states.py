from aiogram.fsm.state import State, StatesGroup


class Checkout(StatesGroup):
    mail_address = State()
    mail_recipient_name = State()
    mail_recipient_phone = State()
    mail_recipient_email = State()


class AdminAddProduct(StatesGroup):
    pick_category = State()
    pick_brand = State()
    new_brand_name = State()
    new_brand_description = State()
    pick_model = State()
    new_model_name = State()
    new_model_photo = State()
    new_model_description = State()
    product_name = State()
    product_price = State()
    product_description = State()
    product_photo = State()


class AdminEdit(StatesGroup):
    awaiting_value = State()
    awaiting_photo = State()
