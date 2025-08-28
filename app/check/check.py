from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards import client as k
from app import get_message
from data import User



router = Router()



@router.callback_query(k.Menu_callback.filter(F.menu == 'check'))
async def check(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    user_id = call.from_user.id
    user = (await User.create(user_id=user_id))[0]

    kb = k.cancel_kb()

    text = get_message(code='check', lang=user.lang)
    kb = k.choose_check(lang=user.lang)
    await call.message.answer(text=text, reply_markup=kb)


@router.message(F.text.contains('Check'))
@router.message(F.text.contains('Проверить'))
async def check(message: Message, state: FSMContext):

    if state:
        await state.clear()

    user_id = message.from_user.id
    user = (await User.create(user_id=user_id))[0]

    text = get_message(code='preparation', lang=user.lang)
    kb = k.cancel_kb(lang=user.lang)
    await message.answer(text=text, reply_markup=kb)

    text = get_message(code='check', lang=user.lang)
    kb = k.choose_check(lang=user.lang)
    await message.answer(text=text, reply_markup=kb)