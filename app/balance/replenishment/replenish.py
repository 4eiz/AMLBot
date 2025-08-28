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



@router.callback_query(k.Menu_callback.filter(F.menu == 'replenish'))
async def rep1(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    user_id = call.from_user.id
    user = (await User.create(user_id=user_id))[0]

    text = get_message(code='replenish_1', lang=user.lang)
    
    await call.message.answer(text=text)
    await state.set_state(CryproBot.sum)



@router.message(F.text.contains('Replenish'))
@router.message(F.text.contains('Пополнить'))
async def rep1(message: Message, state: FSMContext):

    if state:
        await state.clear()

    user_id = message.from_user.id
    user = (await User.create(user_id=user_id))[0]

    text = get_message(code='preparation', lang=user.lang)
    kb = k.cancel_kb(lang=user.lang)
    await message.answer(text=text, reply_markup=kb)

    text = get_message(code='replenish_1', lang=user.lang)
    await message.answer(text=text)

    await state.set_state(CryproBot.sum)