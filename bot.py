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
    value: str


#logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


liquids = get_liquids()
liquids_name = {}
liquids_mg_keyboard = InlineKeyboardBuilder()
liquids_keyboard = InlineKeyboardBuilder()
liquids_taste_keyboard = InlineKeyboardBuilder()


for mg in liquids:
    print(mg)
    liquids_mg_keyboard.button(text=mg, callback_data=CallbackFactory(action="mg", value=mg))

liquids_mg_keyboard.adjust(1)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    await message.answer(
        'text',
        reply_markup=liquids_mg_keyboard.as_markup()
    )

liq_mg = ''
liq_name = ''
liq_taste = ''
@dp.callback_query(CallbackFactory.filter())
async def callbacks_num_change_fab(callback: types.CallbackQuery, callback_data: CallbackFactory):

    if callback_data.action == 'mg':
        liq_mg = callback_data.value
        for name in liquids[callback_data.value]:
            print(name)
            liquids_keyboard.button(text=name, callback_data=CallbackFactory(action='name', value=name))
    if callback_data.action == 'name':
        liq_name = callback_data.value
        for taste in liquids[liq_mg][callback_data.value]:
            print(taste)
            liquids_keyboard.button(text=taste[0], callback_data=CallbackFactory(action='taste', value=taste))

    liq = liq_mg + ' ' + liq_name + ' ' + liq_taste

    liquids_keyboard.adjust(1)
    await callback.message.edit_text(
        liq,
        reply_markup=liquids_keyboard.as_markup()
    )
    await callback.answer()


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
