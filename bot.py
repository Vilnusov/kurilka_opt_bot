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


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


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
    builder.adjust(1)
    return builder


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выбери, что хочешь заказать:", reply_markup=get_main_keyboard().as_markup())


@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    await message.answer_photo(
        'https://kalix.club/uploads/posts/2022-12/1671755316_kalix-club-p-veip-art-oboi-66.jpg',
        'Выберите крепкость и объем жидкости:',
        reply_markup=get_liquids_mg_keyboard().as_markup()
    )


@dp.callback_query(CallbackFactory.filter())
async def callbacks_change_liquids_keyboard(callback: types.CallbackQuery, callback_data: CallbackFactory):
    global liq_mg
    global liq_name
    global liq_taste
    text = '='
    builder = InlineKeyboardBuilder()

    if callback_data.action == 'back':
        if callback_data.value == 'liquids':
            builder = get_main_keyboard()
        elif callback_data.value == 'mg':
            callback_data.action = 'liquids'
        elif callback_data.value == 'name':
            callback_data.action = 'mg'
            callback_data.value = liq_mg

    if callback_data.action == 'liquids':
        text = 'Выберите крепкость и объем жидкости:'
        builder = get_liquids_mg_keyboard()
    elif callback_data.action == 'mg':
        text = 'Выберите жидкость:'
        if callback_data.action == callback_data.value:
            callback_data.value = liq_mg
        liq_mg = callback_data.value
        for name in liquids[callback_data.value]:
            builder.button(text=name, callback_data=CallbackFactory(action='name', value=name))
    elif callback_data.action == 'name':
        text = 'Выберите вкус жидкости:'
        liq_name = callback_data.value
        for taste in liquids[liq_mg][callback_data.value]:
            builder.button(text=taste[0], callback_data=CallbackFactory(action='taste', value=taste[0]))
    elif callback_data.action == 'taste':
        liq_taste = callback_data.value


    builder.button(text='🔙Назад', callback_data=CallbackFactory(action='back', value=callback_data.action))
    builder.adjust(1)
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup()
    )
    await callback.answer()


async def main():
    print('start')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def get_res():
    global liquids
    while True:
        liquids = get_liquids()
        print(liquids)
        await asyncio.sleep(10)


async def tasks():
    print('t')
    task = asyncio.create_task(get_res())
    await task


def m():
    print('m')
    asyncio.run(main())
    asyncio.run(tasks())


if __name__ == "__main__":
    scheduler = AsyncIOScheduler()
    scheduler.add_job(m())
    scheduler.start()
