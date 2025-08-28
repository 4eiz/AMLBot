import asyncio

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards import client as k
from app import get_message, CheckTransaction
from app import aml_api as api
from data import User
from config import bot



router = Router()



@router.callback_query(k.Menu_callback.filter(F.menu == 'check_transaction'))
async def check_transaction_start(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):
    user_id = call.from_user.id
    user = (await User.create(user_id=user_id))[0]

    text = get_message(code='search0', lang=user.lang)
    networks = await api.get_networks(action='address')

    kb = k.choose_network_kb(menu='check_transaction', networks=networks)
    await call.message.answer(text=text, reply_markup=kb)

    await state.set_state(CheckTransaction.network)



@router.callback_query(k.Crypto_callback.filter(F.menu == "check_transaction"), CheckTransaction.network)
async def select_network(call: CallbackQuery, callback_data: k.Crypto_callback, state: FSMContext):

    user_id = call.from_user.id
    user = (await User.create(user_id=user_id))[0]

    network = callback_data.crypto
    await state.update_data(network=network)

    tokens = await api.get_tokens(network)
    # print(tokens)
    if tokens:
        await state.update_data(tokens=tokens)  # Сохраняем список токенов в состоянии

        # Запрашиваем направление транзакции
        # kb = k.choose_direction_kb(lang=user.lang)
        # text = get_message(code='search3', lang=user.lang)

        # await call.message.answer(text=text, reply_markup=kb)
        # await state.set_state(CheckTransaction.token)

        kb = k.choose_token_kb(menu='check_transaction_token', tokens=tokens)
        text = get_message(code='search1', lang=user.lang)

        await call.message.answer(text=text, reply_markup=kb)
        await state.set_state(CheckTransaction.direction)
    else:

        text = get_message(code='search_error1', lang=user.lang)
        await call.message.answer(text=text)

        await state.clear()



@router.callback_query(k.Crypto_callback.filter(F.menu == "check_transaction_token"), CheckTransaction.token)
async def select_token(call: CallbackQuery, callback_data: k.Crypto_callback, state: FSMContext):

    user_id = call.from_user.id
    user = (await User.create(user_id=user_id))[0]

    token_index = int(callback_data.crypto)  # Получаем индекс токена
    data = await state.get_data()
    tokens = data.get("tokens")  # Получаем список токенов из состояния

    if tokens and 0 <= token_index < len(tokens):
        token_id, symbol, name = tokens[token_index]
        await state.update_data(token_id=token_id)

        # Запрашиваем направление транзакции
        kb = k.choose_direction_kb(lang=user.lang)
        text = get_message(code='search3', lang=user.lang)

        await call.message.answer(text=text, reply_markup=kb)

        await state.set_state(CheckTransaction.direction)
    else:

        text = get_message(code='search_error1', lang=user.lang)
        await call.message.answer(text=text)

        await state.clear()


@router.callback_query(k.Crypto_callback.filter(F.menu == "check_transaction_direction"), CheckTransaction.direction)
async def select_direction(call: CallbackQuery, callback_data: k.Crypto_callback, state: FSMContext):

    user_id = call.from_user.id
    user = (await User.create(user_id=user_id))[0]

    direction = callback_data.crypto  # "incoming" или "outgoing"
    await state.update_data(direction=direction)

    text = get_message(code='search4', lang=user.lang)
    await call.message.answer(text=text)

    await state.set_state(CheckTransaction.tx_hash)



@router.message(CheckTransaction.tx_hash)
async def enter_tx_hash(message: Message, state: FSMContext):

    user_id = message.from_user.id
    user = (await User.create(user_id=user_id))[0]

    tx_hash = message.text
    await state.update_data(tx_hash=tx_hash)

    text = get_message(code='search5', lang=user.lang)
    await message.answer(text=text)

    data = await state.get_data()
    network = (data.get("network"))
    print(f'network | {network}')
    tokens = await api.get_tokens(network=network)
    print(tokens)

    symbol = await api.get_token_symbol(hash=tx_hash, network=network)
    print(f'symbol | {symbol}')
    token_id = await api.get_token_by_symbol(symbol=symbol, network=network)
    print(f'token_id | {token_id}')

    await state.update_data(token_id=token_id)

    await state.set_state(CheckTransaction.output_address)



@router.message(CheckTransaction.output_address)
async def enter_output_address(message: Message, state: FSMContext):

    user_id = message.from_user.id
    user = (await User.create(user_id=user_id))[0]

    output_address = message.text
    data = await state.get_data()

    network = data.get("network")
    token_id = data.get("token_id")
    direction = data.get("direction")
    tx_hash = data.get("tx_hash")

    try:
        await user.update_balance(amount=-1)
        # print(balance_status)
    except Exception:
        text = get_message('balance_error1', lang=user.lang)
        await message.answer(text=text)

        await state.clear()
        return

    # Проверяем транзакцию через API
    transaction_check = await api.check_transaction(network, token_id, tx_hash, output_address, direction)
    if not transaction_check or 'id' not in transaction_check:
        text = get_message(code='search_error500')
        await message.answer(text=text)
        return

    text = get_message(code='search_info', lang=user.lang)
    await message.answer(text=text)

    transaction_id = transaction_check['id']
    wait = 1

    while True:
        result = await api.get_check_by_id(check_id=transaction_id)
        if result.get('check_status') == 'checked':
            break

        print(f'Ожидание | {wait}')
        await asyncio.sleep(5)
        wait += 1

    # print(result)

    if not result:
        text = get_message('search_error500', lang=user.lang)
        await message.answer(text=text)
        await state.clear()
        return

    # Форматируем результат
    risks = result.get('risks', [])
    risk_types = ', '.join([risk['type'] for risk in risks]) if risks else "<code>None</code>"
    risk_level = result.get('risk_level')
    risk_score = result.get('risk_score')
    fiat_currency = result.get('fiat_currency')
    check_status = result.get('check_status')
    checked_at = result.get('checked_at')

    # Форматируем данные об экспозиции
    exposure = result.get('exposure', [])
    exposure_details = "\n".join(
        [f"- <b>{item['entity_category']}</b>: <code>{item['value_share'] * 100:.2f}%</code>"
         for item in exposure]
    ) if exposure else "<code>None</code>"

    me = await bot.me()
    bot_username = me.username

    text = get_message(
        code='result_transaction',
        lang=user.lang,
        network=network,
        token_id=token_id,
        tx_hash=tx_hash,
        output_address=output_address,
        direction=direction,
        risk_level=risk_level,
        risk_score=risk_score,
        fiat_currency=fiat_currency,
        risk_types=risk_types,
        exposure_details=exposure_details,
        check_status=check_status,
        checked_at=checked_at,
        bot_username=bot_username
    )
    await message.reply(text=text)

    await state.clear()