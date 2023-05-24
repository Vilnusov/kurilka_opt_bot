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


class NumbersCallbackFactory(CallbackData, prefix="my"):
    value: str


#logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


liquids_name = InlineKeyboardBuilder()
liquids_taste = InlineKeyboardBuilder()


for name in get_liquids():
    print(name[0])
    liquids_name.button(InlineKeyboardButton(text=name[0], callback_data=NumbersCallbackFactory(value=name[0])))

liquids_name.adjust(1)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    await message.answer(
        'text',
        reply_markup=liquids_name.as_markup()
    )


@dp.callback_query(NumbersCallbackFactory.filter())
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: NumbersCallbackFactory
):
    await callback.message.edit_text(
        callback_data.value,
    )
    await callback.answer()

@dp.callback_query(Text("name"))
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.edit_text(
        'asd'
    )
    await callback.answer()


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
