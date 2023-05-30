from cfg import *
from getter import get_liquids
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from aiogram.enums.parse_mode import ParseMode


class CallbackFactory(CallbackData, prefix="my"):
    action: str
    value: Optional[str]


# 'https://kalix.club/uploads/posts/2022-12/1671755316_kalix-club-p-veip-art-oboi-66.jpg'
# logging.basicConfig(level=logging.INFO)
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


@dp.message(Command("test"))
async def cmd_numbers(message: types.Message):
    button_text = 'Текст кнопки'
    builder = InlineKeyboardBuilder()
    builder.button(text=f"~{button_text}~", callback_data='asd')
    await message.answer("Текст с ~зачеркнутой~ кнопкой", reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Добавить проверку
    user_data[message.from_user.username] = [1]
    await message.answer(
        f"{message.from_user.full_name}, Добро пожаловать\nВыбери, что хочешь заказать или просмотри свой заказ:",
        reply_markup=get_main_keyboard().as_markup()
    )


@dp.message(Command("admin"))
async def cmd_start(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        result = ''
        for order in user_data:
            result += f'{order} :\n\t{user_data[order]}'
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
        elif callback_data.value in ['taste', 'num_decr', 'num_incr']:
            callback_data.action = 'name'
            callback_data.value = liq_name
            user_data[callback.from_user.username][0] = 1

    if callback_data.action == 'del':
        text = get_cart(callback.from_user.username)
        text += '\nВведите номер позиции, которую хотите удалить:'
    if callback_data.action == 'cart':
        if get_cart(callback.from_user.username) != '\nИтого: 0 BYN':
            text = get_cart(callback.from_user.username)
            builder.button(text='Удалить позицию', callback_data=CallbackFactory(action='del'))
        else:
            text = 'Вы еще ничего не добвили в корзину!'

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
            txt = ''
            if not taste[1]:
                txt = '⛔️'
            txt += taste[0]
            if len(f'my:taste:{txt}'.encode()) > 64:
                while len(f'my:taste:{txt}'.encode()) > 61:
                    txt = txt[:-1]
                txt += '...'
            builder.button(text=txt, callback_data=CallbackFactory(action='taste', value=txt))
    elif callback_data.action == 'taste':
        if '⛔️' in callback_data.value:
            await callback.answer(
                text="Данной жидкости нет в наличии!",
                show_alert=True
            )
            return
        text = 'Укажите количество: 1'
        builder = get_counter_keyboard()
        liq_taste = callback_data.value

    if callback_data.action == 'num_decr':
        if user_data[callback.from_user.username][0] == 1:
            await callback.answer(
                text="Количество не может быть меньше одного!",
                show_alert=True
            )
            return
        else:
            user_data[callback.from_user.username][0] -= 1
        text += f'Укажите количество: {user_data[callback.from_user.username][0]}'
        builder = get_counter_keyboard()
    elif callback_data.action == 'num_incr':
        user_data[callback.from_user.username][0] += 1
        text = f'Укажите количество: {user_data[callback.from_user.username][0]}'
        builder = get_counter_keyboard()
    elif callback_data.action == 'num_confirm':
        user_data[callback.from_user.username].append([liq_name + ' ' + liq_taste,
                                                       user_data[callback.from_user.username][0],
                                                       liquids[liq_mg][liq_name][0][2]]
                                                      )
        user_data[callback.from_user.username][0] = 1
        await callback.message.edit_text(
            text='Жидкость добавлена!\nВыбери, что хочешь заказать или просмотри свой заказ:',
            reply_markup=get_main_keyboard().as_markup()
        )
        return

    builder.button(text='🔙Назад', callback_data=CallbackFactory(action='back', value=callback_data.action))
    builder.adjust(1)
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup()
    )
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
        if user_data[username].index(item) == 0:
            continue
        res += f'{user_data[username].index(item)}. {item[0]} - {item[1]}шт - {item[2]} BYN\n'
        price += float('.'.join(item[2].split(',')))
    res += f'\nИтого: {price} BYN'
    return res


if __name__ == "__main__":
    asyncio.run(main())
