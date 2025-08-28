import os
from dotenv import load_dotenv

from aiogram.types import CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from keyboards import client as k
from data import User
from app import get_message
from config import bot




router = Router()




@router.callback_query(k.Menu_callback.filter(F.menu == 'change_language'))
async def set_language(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    text = '''
Выберите язык
Select language
'''
    kb = k.lang_kb()

    await call.message.answer(text=text, reply_markup=kb)


@router.callback_query(k.Langauge_callback.filter(F.menu == 'lang'))
async def set_language(call: CallbackQuery, callback_data: k.Langauge_callback, state: FSMContext):

    user_id = call.from_user.id
    user = (await User.create(user_id=user_id))[0]
    
    language = callback_data.lang
    await user.update_language(new_lang=language)

    # sub_status = await check_sub(message=call.message)
    # if sub_status == False:
    #     return

    text = get_message(code='menu', lang=language)
    kb = k.menu_kb(lang=language)
    await call.message.answer(text=text, reply_markup=kb)