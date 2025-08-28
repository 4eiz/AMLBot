import asyncio
import logging
from aiogram import Dispatcher

from config import bot
from data.main import script

from app import start, change_language, promo
from app.balance import balance
from app.balance.replenishment import replenish, cb
from app.check import check, check_adress, check_transaction
from app.profile import profile, referral, support



async def start_bot():
    dp = Dispatcher()

    dp.include_routers(
        start.router,
        change_language.router,
        balance.router,
        replenish.router,
        cb.router,
        check.router,
        check_adress.router,
        check_transaction.router,
        profile.router,
        referral.router,
        support.router,
        promo.router,
    )

    await script()
    
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())
