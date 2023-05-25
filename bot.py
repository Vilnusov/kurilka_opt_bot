from random import random
from pprint import pprint
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


#logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


liq_mg = ''
liq_name = ''
liq_taste = ''
liquids = []


def get_liquids_mg_keyboard():
    global liquids
    builder = InlineKeyboardBuilder()
    liquids = get_liquids()
    for mg in liquids:
        print(mg)
        builder.button(text=mg, callback_data=CallbackFactory(action="mg", value=mg))
    builder.adjust(2)
    return builder


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!\nНапиши /random")


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
    builder = InlineKeyboardBuilder()
    if callback_data.action == 'back':
        callback_data.action = 'mg'
        callback_data.value = 'Salt 50mg | Объем 30мл'
    if callback_data.action == 'mg':
        liq_mg = callback_data.value
        for name in liquids[callback_data.value]:
            print(name)
            builder.button(text=name, callback_data=CallbackFactory(action='name', value=name))
    elif callback_data.action == 'name':
        liq_name = callback_data.value
        for taste in liquids[liq_mg][callback_data.value]:
            print(taste)
            builder.button(text=taste[0], callback_data=CallbackFactory(action='taste', value=taste[0]))
    elif callback_data.action == 'taste':
        liq_taste = callback_data.value


    liq = liq_mg + ' ' + liq_name + ' ' + liq_taste

    builder.adjust(2)

    builder.button(text='🔙Назад', callback_data=CallbackFactory(action='back'))
    await callback.message.edit_caption(
        caption=liq,
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(Text("back"))
async def go_back(callback: types.CallbackQuery):
    await callback


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
