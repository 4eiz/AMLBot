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



@router.callback_query(k.Menu_callback.filter(F.menu == 'support'))
async def support(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    user_id = call.from_user.id
    user = (await User.create(user_id=user_id))[0]

    text = get_message(code='support', lang=user.lang)
    await call.message.answer(text=text)