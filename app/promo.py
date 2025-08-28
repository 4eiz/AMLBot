from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from data import PromoCode

router = Router()

@router.message(Command("add_promo"))
async def add_promo(message: Message):
    # Проверяем, что команда введена правильно
    try:
        _, promo_name, discount_percent, expiration_date = message.text.split()
        discount_percent = float(discount_percent)
    except ValueError:
        text = "Неправильный формат команды. Используйте: /add_promo название скидка дата_окончания"
        await message.answer(text=text)
        return

    # Проверяем, что дата введена в правильном формате
    try:
        datetime.strptime(expiration_date, "%Y-%m-%d")
    except ValueError:
        text = "Неправильный формат даты. Используйте формат: yyyy-mm-dd"
        await message.answer(text=text)
        return

    # Добавляем промокод в базу данных
    try:
        if await PromoCode.create(promo_name, discount_percent, expiration_date):
            text = f"Промокод '{promo_name}' успешно добавлен!"
            await message.answer(text=text)
        else:
            text = "Ошибка при добавлении промокода."
            await message.answer(text=text)
    except Exception as e:
        text = f"Ошибка: {e}"
        await message.answer(text=text)
        return