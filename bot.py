from random import random
from pprint import pprint

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from cfg import *
from getter import get_liquids
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Optional
from aiogram.filters.callback_data import CallbackData


class CallbackFactory(CallbackData, prefix="my"):
    action: str
    value: Optional[str]


#'https://kalix.club/uploads/posts/2022-12/1671755316_kalix-club-p-veip-art-oboi-66.jpg'
#logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}
liq_mg = ''
liq_name = ''
liq_taste = ''
liquids = []


def get_liquids_mg_keyboard():
    global liquids
    builder = InlineKeyboardBuilder()
    for mg in liquids:
        builder.button(text=mg, callback_data=CallbackFactory(action="mg", value=mg))
    builder.adjust(1)
    return builder


def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='Жидкости', callback_data=CallbackFactory(action='liquids'))
    builder.button(text='Расходники', callback_data=CallbackFactory(action='ras'))
    builder.button(text='🗑Корзина', callback_data=CallbackFactory(action='cart'))
    builder.adjust(2, 1)
    return builder


def get_counter_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='-1', callback_data=CallbackFactory(action='num_decr'))
    builder.button(text='+1', callback_data=CallbackFactory(action='num_incr'))
    builder.button(text='Подтвердить', callback_data=CallbackFactory(action='num_confirm'))
    builder.adjust(2, 1)
    return builder


@dp.message(Command("num"))
async def cmd_numbers(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("Укажите количество: 1", reply_markup=get_counter_keyboard().as_markup())


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    #Добавить проверку
    user_data[message.from_user.username] = [None] * 3
    await message.answer(
        f"{message.from_user.full_name}, Добро пожаловать\nВыбери, что хочешь заказать или просмотри свой заказ:",
        reply_markup=get_main_keyboard().as_markup()
    )


@dp.message(Command("admin"))
async def cmd_start(message: types.Message):
    if message.from_user.id in ADMINS:
        result = ''
        for order in user_data:
            result += order + ':\n\t' + str(user_data[order])
        await message.answer(
            f"Заказы:\n{result}"
        )


@dp.callback_query(CallbackFactory.filter())
async def callbacks_change_liquids_keyboard(callback: types.CallbackQuery, callback_data: CallbackFactory):
    global liq_mg
    global liq_name
    global liq_taste
    text = '='
    builder = InlineKeyboardBuilder()

    if callback_data.action == 'back':
        if callback_data.value == 'liquids' or callback_data.value == 'cart':
            await callback.message.edit_text(
                'Выбери, что хочешь заказать или просмотри свой заказ:',
                reply_markup=get_main_keyboard().as_markup()
            )
            return
        elif callback_data.value == 'mg':
            callback_data.action = 'liquids'
        elif callback_data.value == 'name':
            callback_data.action = 'mg'
            callback_data.value = liq_mg

    if callback_data.action == 'cart':
        if len(get_cart(callback.from_user.username)) != 0:
            text = get_cart(callback.from_user.username)
        else:
            text = 'Вы еще ничего не добвили в корзину!'

    if callback_data.action == 'num_decr':
        if user_data[callback.from_user.username][1] is None:
            user_data[callback.from_user.username][1] = 1
        user_data[callback.from_user.username][1] -= 1
        text = f'Укажите количество: {user_data[callback.from_user.username][1]}'
        builder = get_counter_keyboard()
    elif callback_data.action == 'num_incr':
        if user_data[callback.from_user.username][1] is None:
            user_data[callback.from_user.username][1] = 1
        user_data[callback.from_user.username][1] += 1
        text = f'Укажите количество: {user_data[callback.from_user.username][1]}'
        builder = get_counter_keyboard()
    elif callback_data.action == 'num_confirm':
        pass

    if callback_data.action == 'liquids':
        text = 'Выберите крепкость и объем жидкости:'
        builder = get_liquids_mg_keyboard()
    elif callback_data.action == 'mg':
        text = 'Выберите жидкость:'
        liq_mg = callback_data.value
        for name in liquids[callback_data.value]:
            builder.button(
                text=name + ' - ' + liquids[callback_data.value][name][0][2] + 'BYN',
                callback_data=CallbackFactory(action='name', value=name)
            )
    elif callback_data.action == 'name':
        text = 'Выберите вкус жидкости:'
        liq_name = callback_data.value
        for taste in liquids[liq_mg][callback_data.value]:
            builder.button(text=taste[0], callback_data=CallbackFactory(action='taste', value=taste[0]))
    elif callback_data.action == 'taste':
        text = 'Укажите количество: 1'
        builder = get_counter_keyboard()
        liq_taste = callback_data.value

        user_data[callback.from_user.username].append([liq_name + ' ' + liq_taste, 0, liquids[liq_mg][liq_name][0][2]])
        #await callback.message.edit_text(text='Жидкость добавлена', reply_markup=get_main_keyboard().as_markup())
        #return

    builder.button(text='🔙Назад', callback_data=CallbackFactory(action='back', value=callback_data.action))
    builder.adjust(1)
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup()
    )
    await callback.answer()


async def update_num_text(message: types.Message, new_value: int):
    await message.edit_text(
        f"Укажите число: {new_value}",
        reply_markup=get_counter_keyboard().as_markup()
    )


@dp.callback_query(Text(startswith="num_"))
async def callbacks_num(callback: types.CallbackQuery):
    user_value = user_data.get(callback.from_user.id, 1)
    print(user_data)
    action = callback.data.split("_")[1]

    if action == "incr":
        user_data[callback.from_user.id] = user_value+1
        await update_num_text(callback.message, user_value+1)
    elif action == "decr":
        user_data[callback.from_user.id] = user_value-1
        await update_num_text(callback.message, user_value-1)
    elif action == "finish":
        await callback.message.edit_text(f"Итого: {user_value}")

    await callback.answer()


async def main():
    asyncio.create_task(get_res())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def get_res():
    global liquids
    while True:
        liquids = get_liquids()
        await asyncio.sleep(10)


def get_cart(username):
    res = ''
    price = 0
    for item in user_data[username]:
        res += str(user_data[username].index(item) + 1) + '. ' + item[0] + ' - ' + str(item[1]) + 'шт - ' + item[2] + 'BYN\n'
        price += float('.'.join(item[2].split(',')))
    res += f'\nВсего: {price} BYN'
    return res


if __name__ == "__main__":
    asyncio.run(main())
