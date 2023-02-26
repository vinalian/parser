from aiogram.fsm.state import State, StatesGroup


class Sub_paying(StatesGroup):
    action = State()
    price = State()
    time = State()
    secret_key = State()


class Edit_mailing_price(StatesGroup):
    price = State()
