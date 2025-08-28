import os
from dotenv import load_dotenv

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from typing import Optional, List, Dict
from datetime import datetime, timedelta

from app import get_button



load_dotenv()
channel_url = os.getenv("channel_url")



class Menu_callback(CallbackData, prefix="menu"):
    menu: str

class Crypto_callback(CallbackData, prefix="crypto"):
    menu: str
    crypto: str


class Langauge_callback(CallbackData, prefix="menu"):
    menu: str
    lang: str




def lang_kb():

    kb = [
        [
            InlineKeyboardButton(text='🇷🇺 Russian', callback_data=Langauge_callback(menu='lang', lang='ru').pack()),
        ],
        [
            InlineKeyboardButton(text='🇺🇸 English', callback_data=Langauge_callback(menu='lang', lang='en').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


# def menu_kb(lang):

#     keyboard = 'menu'
#     check = get_button(keyboard=keyboard, button='check', lang=lang)
#     balance = get_button(keyboard=keyboard, button='balance', lang=lang)
#     account = get_button(keyboard=keyboard, button='account', lang=lang)
#     replenish = get_button(keyboard=keyboard, button='replenish', lang=lang)

#     kb = [
#         [
#             InlineKeyboardButton(text=f'{check}', callback_data=Menu_callback(menu='check').pack()),
#         ],
#         [
#             InlineKeyboardButton(text=f'{balance}', callback_data=Menu_callback(menu='balance').pack()),
#         ],
#         [
#             InlineKeyboardButton(text=f'{account}', callback_data=Menu_callback(menu='account').pack()),
#         ],
#         [
#             InlineKeyboardButton(text=f'{replenish}', callback_data=Menu_callback(menu='replenish').pack()),
#         ],
#     ]

#     return InlineKeyboardMarkup(inline_keyboard=kb)


def menu_kb(lang, is_admin=False):

    keyboard = 'menu'
    check = get_button(keyboard=keyboard, button='check', lang=lang)
    balance = get_button(keyboard=keyboard, button='balance', lang=lang)
    account = get_button(keyboard=keyboard, button='account', lang=lang)
    replenish = get_button(keyboard=keyboard, button='replenish', lang=lang)

    kb = [
        [
            KeyboardButton(text=f'{check}'),
            KeyboardButton(text=f'{balance}'),
        ],
        [
            KeyboardButton(text=f'{account}'),
            KeyboardButton(text=f'{replenish}'),
        ]
    ]

    # if is_admin:
    #     kb.append(
    #         [
    #             KeyboardButton(text=f'🔑 {admin_panel}')
    #         ],
    #     )

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def replenishment_kb(lang):

    keyboard = 'menu'
    replenish = get_button(keyboard=keyboard, button='replenish', lang=lang)
    
    kb = [
        [
            InlineKeyboardButton(text=f'{replenish}', callback_data=Menu_callback(menu="replenish").pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def repl_kb(url, lang):
    
    keyboard = 'replenish'
    cancel = get_button(keyboard=keyboard, button='cancel', lang=lang)

    kb = [
        [
            InlineKeyboardButton(text='Cryptobot', url=url)
        ],
        [
            InlineKeyboardButton(text=f'{cancel}', callback_data=Menu_callback(menu="cancel_invoice").pack())
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def channel_kb(channel_url):

    kb = [
        [
            InlineKeyboardButton(text='Channel', url=channel_url),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


# Клавиатура для выбора сети
def choose_network_kb(menu, networks: list):
    """
    Генерирует клавиатуру для выбора сети, располагая кнопки по 2 в ряд.

    :param networks: Список кортежей.
    :return: InlineKeyboardMarkup с кнопками сетей.
    """
    builder = InlineKeyboardBuilder()
    # print(networks)

    # Добавляем кнопки по 4 в ряд
    for i in range(0, len(networks), 2):
        row = networks[i:i + 2]  # Берем по 4 сети
        buttons = [
            InlineKeyboardButton(
                text=network[0],
                callback_data=Crypto_callback(menu=menu, crypto=network[1]).pack()
            )
            for network in row
        ]
        builder.row(*buttons)

    return builder.as_markup()


# Клавиатура для выбора токена
def choose_token_kb(menu, tokens: list[tuple]):
    """
    Генерирует клавиатуру для выбора токена.

    :param tokens: Список токенов в формате (tokenId, symbol, name).
    :return: InlineKeyboardMarkup с кнопками токенов.
    """
    builder = InlineKeyboardBuilder()

    for index, (token_id, symbol, name) in enumerate(tokens):
        builder.add(
            InlineKeyboardButton(
                text=f"{symbol} ({name})",
                callback_data=Crypto_callback(menu=menu, crypto=str(index)).pack()
            )
        )

    builder.adjust(2)  # Располагаем кнопки по 2 в ряд
    return builder.as_markup()


def choose_check(lang):

    keyboard = 'choose_check'
    adress = get_button(keyboard=keyboard, button='adress', lang=lang)
    transaction = get_button(keyboard=keyboard, button='transaction', lang=lang)

    kb = [
        [
            InlineKeyboardButton(text=f'{adress}', callback_data=Menu_callback(menu="check_address").pack()),
        ],
        [
            InlineKeyboardButton(text=f'{transaction}', callback_data=Menu_callback(menu="check_transaction").pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def choose_direction_kb(lang):

    keyboard = 'choose_transaction'
    incoming = get_button(keyboard=keyboard, button='incoming', lang=lang)
    outgoing = get_button(keyboard=keyboard, button='outgoing', lang=lang)

    kb = [
        [
            InlineKeyboardButton(text=f"{incoming}", callback_data=Crypto_callback(menu="check_transaction_direction", crypto="incoming").pack()),
        ],
        [
            InlineKeyboardButton(text=f"{outgoing}", callback_data=Crypto_callback(menu="check_transaction_direction", crypto="outgoing").pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def account_kb(lang):

    keyboard = 'account'
    support = get_button(keyboard=keyboard, button='support', lang=lang)
    balance = get_button(keyboard=keyboard, button='balance', lang=lang)
    referral = get_button(keyboard=keyboard, button='referral', lang=lang)

    kb = [
        [
            InlineKeyboardButton(text=f"{support}", callback_data=Menu_callback(menu='support').pack()),
            InlineKeyboardButton(text=f"{balance}", callback_data=Menu_callback(menu='balance').pack()),
            InlineKeyboardButton(text=f"{referral}", callback_data=Menu_callback(menu='referral').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)



def cancel_kb(lang: str):

    keyboard = 'menu'
    cancel = get_button(keyboard=keyboard, button='cancel', lang=lang)

    kb = [
        [
            KeyboardButton(text=f'{cancel}'),
        ],
    ]

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)