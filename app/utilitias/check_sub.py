import asyncio
from data import Settings
from config import bot
from keyboards.client import channel_kb


async def check_sub(message):

    user_id = message.from_user.id

    channel_id = await Settings.get_value('subscription_chat_id')
    if channel_id != '':
        sub = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        if sub.status == 'left':
            text = 'Подпишитесь на канал\nSubscribe to the channel'

            channel_url = await Settings.get_value('subscription_chat_link')

            kb = channel_kb(channel_url=channel_url)
            await message.answer(text=text, reply_markup=kb)

            return False
        
        return True