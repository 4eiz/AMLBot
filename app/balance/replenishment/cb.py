import asyncio
import os
from dotenv import load_dotenv

from aiocryptopay import AioCryptoPay
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiocryptopay import AioCryptoPay, Networks

from keyboards import client as k
from config import bot
from app.fsm import CryproBot
from app import get_message

from data import User, PromoCode  # Импортируем класс PromoCode



# Загрузка переменных окружения
CRYPTO_TOKEN = os.getenv('CRYPTO_TOKEN')
price = float(os.getenv('price'))  # Цена за одну штуку
min_price = float(os.getenv('min_price'))  # Минимальная цена за одну штуку
count_to_reduce = int(os.getenv('count_to_reduce'))  # Количество штук для скидки
discount_for_wholesale = float(os.getenv('discount_for_wholesale'))  # Скидка за опт



router = Router()




@router.message(CryproBot.sum)
async def show(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = (await User.create(user_id=user_id))[0]


    # promo = await PromoCode.create(promo_name="TEST2", discount_percent=15.0, expiration_date="2025-03-31")
    # print(f"Создан промокод: {promo.promo_name}, скидка: {promo.discount_percent}%")

    # Получаем количество штук (например, из сообщения пользователя)
    try:
        amount = int(message.text)  # Предположим, что пользователь вводит количество
        await state.update_data(amount=amount)
    except Exception:
        text = get_message(code='replenish_error1', lang=user.lang)
        await message.answer(text=text)
        return

    text = get_message('replenish_2.1', lang=user.lang)
    await message.answer(text=text)

    await state.set_state(CryproBot.promo)


@router.message(CryproBot.promo)
async def apply_promo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = (await User.create(user_id=user_id))[0]

    data = await state.get_data()
    amount = data.get('amount')
    promo_code = message.text.strip()  # Получаем промокод от пользователя

    # Если промокод не указан (пользователь ввел '-'), скидка не применяется
    if promo_code == '-':
        total_price = await user.calculate_price(
            amount, price, min_price, count_to_reduce, discount_for_wholesale
        )
    else:
        # Проверяем промокод
        promo = await PromoCode.get_by_name(promo_code)
        if not promo:
            text = get_message(code='promo_error1', lang=user.lang)
            await message.answer(text=text)
            return

        try:
            discount_percent = await promo.activate()  # Активируем промокод
        except Exception as e:
            text = get_message(code='promo_error3', lang=user.lang)
            await message.answer(text=text)
            return

        # Применяем скидку по промокоду
        total_price = await user.calculate_price(
            amount, price, min_price, count_to_reduce, discount_for_wholesale, discount_percent
        )

    # Отправляем результат пользователю
    text = get_message('replenish_2', lang=user.lang, total_price=total_price)
    await message.answer(text=text)

    crypto = AioCryptoPay(token=CRYPTO_TOKEN, network=Networks.MAIN_NET)
    invoice = await crypto.create_invoice(amount=total_price, fiat='USD', currency_type='fiat')
    text = get_message(code='replenish_3', lang=user.lang)
    kb = k.repl_kb(url=invoice.bot_invoice_url, lang=user.lang)
    mes_rep = await message.answer(text, reply_markup=kb)

    await state.update_data(id=invoice.invoice_id)

    timeout = 60 * 5  # 60 минут
    interval = 5

    while timeout > 0:
        # Проверяем статус платежа
        print(f'[WAIT] {invoice.invoice_id} | Ожидание оплаты')
        payment_status = await check_crypto_bot_invoice(invoice.invoice_id)

        if payment_status:
            await user.update_balance(amount=amount)
            # Платеж выполнен, выполните соответствующие действия
            text = get_message(code='replenish_4', lang=user.lang, amount=amount)
            await message.answer(text)

            await bot.delete_message(chat_id=message.chat.id, message_id=mes_rep.message_id)
            break
        else:
            # Платеж не выполнен, уменьшаем таймаут
            timeout -= interval

        await asyncio.sleep(interval)

    if timeout <= 0:
        # Таймаут истек, отменяем платеж и отправляем сообщение об отмене
        await bot.delete_message(chat_id=message.chat.id, message_id=mes_rep.message_id)
        await crypto.delete_invoice(invoice_id=invoice.invoice_id)

    await state.clear()


@router.callback_query(k.Menu_callback.filter(F.menu == 'cancel_invoice'), CryproBot.promo)
async def cancel_repl(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):
    data = await state.get_data()
    invoice = data.get('id')
    status = await cancel_invoice(invoice=invoice)
    if status:
        text = 'Платёж отменён'
        await call.message.answer(text=text)
        await state.clear()
    else:
        await state.clear()


#-----------------------------


async def check_crypto_bot_invoice(invoice_id: int):
    cryptopay = AioCryptoPay(CRYPTO_TOKEN)
    invoice = await cryptopay.get_invoices(invoice_ids=invoice_id)
    await cryptopay.close()
    return invoice.status == 'paid'


async def cancel_invoice(invoice):
    try:
        crypto = AioCryptoPay(token=CRYPTO_TOKEN, network=Networks.MAIN_NET)
        await crypto.delete_invoice(invoice_id=invoice)
        return True
    except Exception as e:
        print(e)
        return False
