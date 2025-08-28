import os
from dotenv import load_dotenv

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from keyboards import client as k
from data import User
from app import get_message
from config import bot



router = Router()



@router.message(CommandStart())
@router.message(CommandStart(deep_link=True))
async def start(message: Message, state: FSMContext, command: CommandObject):
    if state:
        await state.clear()

    ref_code = command.args
    user_id = message.from_user.id

    # Проверяем, существует ли пользователь в базе данных
    if await User.user_exists(user_id):
        user = (await User.create(user_id=user_id))[0]
        text = get_message(code='menu', lang=user.lang)
        kb = k.menu_kb(lang=user.lang)
        await message.answer(text=text, reply_markup=kb)
        return  # Прерываем выполнение функции, если пользователь уже существует

    try:
        result = await User.create(user_id, ref_code)
        if isinstance(result, tuple):
            if len(result) == 2:  # Проверяем, что кортеж содержит два элемента
                user, referrer_id = result  # Распаковываем кортеж
                print('Реферер найден:', referrer_id)
            else:
                user = result[0]  # Если кортеж содержит только один элемент
                referrer_id = None  # Реферер не найден
                print('Реферер не найден')
                
    except Exception as e:
        print(f"Ошибка: {e}")
        return  # Прерываем выполнение функции, если возникла ошибка

    text = '.'
    kb = k.lang_kb()
    await message.answer(text=text, reply_markup=kb)

    # Отправка уведомления рефералу (если referrer_id определен)
    if referrer_id:  # Проверяем, что referrer_id существует
        try:
            referrer = await User.create(user_id=referrer_id)
            give_check = await referrer.give_free_check()
            username_referal = message.from_user.username

            if give_check[0]:  # Проверяем успешность выдачи проверки
                text = get_message(code='ref1', lang=referrer.lang, name=username_referal)
            else:
                text = get_message(code='ref2', lang=referrer.lang, name=username_referal)

            await bot.send_message(chat_id=referrer.user_id, text=text)
        except Exception as e:
            print(f"Ошибка при отправке уведомления рефералу: {e}")




@router.message(F.text.contains('Cancel'))
@router.message(F.text.contains('Отмена'))
async def cancel_handler(message: Message, state: FSMContext):

    user_id = message.from_user.id
    user = (await User.create(user_id=user_id))[0]

    # Сбрасываем состояние
    await state.clear()

    # Отправляем сообщение с главным меню
    text = get_message(code='menu', lang=user.lang)
    kb = k.menu_kb(lang=user.lang)
    await message.answer(text=text, reply_markup=kb)