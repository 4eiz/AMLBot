from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext



class Buy_order(StatesGroup):
    link = State()
    amount = State()
    confirmation = State()


class CryproBot(StatesGroup):
    sum = State()
    promo = State()


class CheckAddress(StatesGroup):
    network = State()
    token = State()
    address = State()


class CheckTransaction(StatesGroup):
    network = State()  # Выбор сети
    token = State()  # Выбор токена
    direction = State()  # Выбор направления транзакции
    tx_hash = State()  # Ввод хеша транзакции
    output_address = State()  # Ввод адреса получателя (опционально)