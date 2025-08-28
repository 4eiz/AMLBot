from aiocryptopay import AioCryptoPay
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

# from app.ban_check import handle_blocked_user
from keyboards import client as k
from app.fsm import CryproBot
from app import get_message
from data import User



router = Router()



@router.callback_query(k.Menu_callback.filter(F.menu == 'balance'))
async def rep1(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    user_id = call.from_user.id
    user = (await User.create(user_id=user_id))[0]

    text = get_message(code='balance', lang=user.lang, bought_checks=user.bought_checks, free_checks=user.free_checks)
    kb = k.replenishment_kb(lang=user.lang)
    await call.message.answer(text=text, reply_markup=kb)



@router.message(F.text.contains('Balance'))
@router.message(F.text.contains('Баланс'))
async def rep1(message: Message, state: FSMContext):

    if state:
        await state.clear()

    user_id = message.from_user.id
    user = (await User.create(user_id=user_id))[0]

    text = get_message(code='balance', lang=user.lang, bought_checks=user.bought_checks, free_checks=user.free_checks)
    kb = k.replenishment_kb(lang=user.lang)
    await message.answer(text=text, reply_markup=kb)