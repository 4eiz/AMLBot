from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link

from keyboards import client as k
from data import User
from app import get_message
from config import bot



router = Router()




@router.callback_query(k.Menu_callback.filter(F.menu == 'referral'))
async def referral(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    if state:
        await state.clear()

    user_id = call.from_user.id
    user = (await User.create(user_id=user_id))[0]

    ref_code = user.ref_code
    ref_link = await create_start_link(bot, ref_code)
    lang = user.lang

    text = get_message(code='referral_system', lang=lang, link=ref_link)
    
    await call.message.answer(text=text)