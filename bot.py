from aiogram.fsm.storage.memory import MemoryStorage

from cfg import *
from getter import get_liquids, get_ras
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional
from aiogram.filters.callback_data import CallbackData


class CallbackFactory(CallbackData, prefix="my"):
    action: str
    value: Optional[str]


class StateDel(StatesGroup):
    choosing_num = State()


class States(StatesGroup):
    start = State()


# 'https://kalix.club/uploads/posts/2022-12/1671755316_kalix-club-p-veip-art-oboi-66.jpg'
# logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode='HTML')
dp = Dispatcher(storage=storage)

user_data = {}
liquids = []
ras = []


def get_liquids_mg_keyboard():
    global liquids
    builder = InlineKeyboardBuilder()
    for mg in liquids:
        builder.button(text=mg, callback_data=CallbackFactory(action="mg", value=mg))
    builder.adjust(1)
    return builder


def get_ras_type_keyboard():
    global ras
    builder = InlineKeyboardBuilder()
    for type in ras:
        builder.button(text=type, callback_data=CallbackFactory(action="type", value=type))
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


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
        # Добавить проверку
        liq_mg = ''
        liq_name = ''
        liq_taste = ''
        ras_type = ''
        ras_proizv = ''
        ras_device = ''
        add = bool
        count = 1
        id_msg = 1
        user_data[message.from_user.username] =\
            [[count, id_msg, liq_mg, liq_name, liq_taste, ras_type, ras_proizv, ras_device, add], []]
        await message.answer(
            f"{message.from_user.full_name}, Добро пожаловать\nВыбери, что хочешь заказать или просмотри свой заказ:",
            reply_markup=get_main_keyboard().as_markup()
        )


@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        result = ''
        price = 0
        for order in user_data:
            price_user = 0
            result += f'\n\n{order} :'
            for item in user_data[order][1]:
                result += f'\n\t{item[0]} - {item[1]}шт'
                price_user += float('.'.join(item[2].split(','))) * item[1]
                price += float('.'.join(item[2].split(','))) * item[1]
            result += f'\n{price_user} BYN'
        result += f'\n\nВсего: {price} BYN'
        await message.answer(
            f"{result}", parse_mode=None
        )


@dp.message(Command("list"))
async def cmd_admin(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        result = ''
        for order in user_data:
            for item in user_data[order][1]:
                result += f'\n{item[0]} - {item[1]}шт'
        await message.answer(
            f"{result}", parse_mode=None
        )


@dp.callback_query(CallbackFactory.filter())
async def callbacks_change_liquids_keyboard(callback: types.CallbackQuery, callback_data: CallbackFactory,
                                            state: FSMContext):
    liq_mg = user_data[callback.from_user.username][0][2]
    liq_name = user_data[callback.from_user.username][0][3]
    liq_taste = user_data[callback.from_user.username][0][4]
    ras_type = user_data[callback.from_user.username][0][5]
    ras_proizv = user_data[callback.from_user.username][0][6]
    ras_device = user_data[callback.from_user.username][0][7]
    add = user_data[callback.from_user.username][0][8]
    text = ''
    builder = InlineKeyboardBuilder()

    # Назад
    if callback_data.action == 'back':
        if callback_data.value == 'liquids' or callback_data.value == 'ras' or callback_data.value == 'cart':
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
            user_data[callback.from_user.username][0][0] = 1
        elif callback_data.value == 'type':
            callback_data.action = 'ras'
        elif callback_data.value == 'device':
            callback_data.action = 'type'
            callback_data.value = ras_type
        elif callback_data.value in ['dev', 'num_decr', 'num_incr']:
            callback_data.action = 'device'
            callback_data.value = ras_proizv
            user_data[callback.from_user.username][0][0] = 1
        elif callback_data.value == 'del':
            await state.set_state()
            callback_data.action = 'cart'

    # Удаление
    if callback_data.action == 'del':
        text = get_cart(callback.from_user.username)
        text += '\n\nВведите номер позиции, которую хотите удалить:'
        callback_data.value = 'del'
        user_data[callback.from_user.username][0][1] = callback.message.message_id
        await state.set_state(StateDel.choosing_num)

    # Корзина
    if callback_data.action == 'cart':
        if get_cart(callback.from_user.username) != '\nИтого: 0 BYN':
            text = get_cart(callback.from_user.username)
            builder.button(text='Удалить позицию', callback_data=CallbackFactory(action='del'))
        else:
            text = 'Вы еще ничего не добвили в корзину!'

    # жидкости
    if callback_data.action == 'liquids':
        text = 'Выберите крепкость и объем жидкости:'
        builder = get_liquids_mg_keyboard()
    elif callback_data.action == 'mg':
        text = 'Выберите жидкость:'
        user_data[callback.from_user.username][0][2] = callback_data.value
        for name in liquids[callback_data.value]:
            builder.button(
                text=name + ' - ' + liquids[callback_data.value][name][0][2] + 'BYN',
                callback_data=CallbackFactory(action='name', value=name)
            )
    elif callback_data.action == 'name':
        text = 'Выберите вкус жидкости:'
        user_data[callback.from_user.username][0][3] = callback_data.value
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
        user_data[callback.from_user.username][0][8] = True
        user_data[callback.from_user.username][0][4] = callback_data.value

    # расходники
    if callback_data.action == 'ras':
        text = 'Выберите тип расходника:'
        builder = get_ras_type_keyboard()
    elif callback_data.action == 'type':
        text = 'Выберите производителя:'
        user_data[callback.from_user.username][0][5] = callback_data.value
        for proizv in ras[callback_data.value]:
            builder.button(
                text=proizv,
                callback_data=CallbackFactory(action='device', value=proizv)
            )
    elif callback_data.action == 'device':
        text = 'Выберите устройство:'
        user_data[callback.from_user.username][0][6] = callback_data.value
        for device in ras[ras_type][callback_data.value]:
            txt = ''
            if not device[2]:
                txt = '⛔️'
            txt += f'{device[0]} {device[1]}Ом {device[3]}BYN'
            builder.button(text=txt, callback_data=CallbackFactory(action='dev', value=txt))
    elif callback_data.action == 'dev':

        if '⛔️' in callback_data.value:
            await callback.answer(
                text="Данного расходника нет в наличии!",
                show_alert=True
            )
            return
        text = 'Укажите количество: 1'
        builder = get_counter_keyboard()
        user_data[callback.from_user.username][0][8] = False
        user_data[callback.from_user.username][0][7] = callback_data.value

    # Кол-во
    if callback_data.action == 'num_decr':
        if user_data[callback.from_user.username][0][0] == 1:
            await callback.answer(
                text="Количество не может быть меньше одного!",
                show_alert=True
            )
            return
        else:
            user_data[callback.from_user.username][0][0] -= 1
        text += f'Укажите количество: {user_data[callback.from_user.username][0][0]}'
        builder = get_counter_keyboard()
    elif callback_data.action == 'num_incr':
        user_data[callback.from_user.username][0][0] += 1
        text = f'Укажите количество: {user_data[callback.from_user.username][0][0]}'
        builder = get_counter_keyboard()
    elif callback_data.action == 'num_confirm':
        add_state = True
        ras_device_arr = [''] * 4
        if ras_device != '':
            for item in ras[ras_type][ras_proizv]:
                if item[0] + ' ' + item[1] in ras_device:
                    ras_device_arr = item
        for item in user_data[callback.from_user.username][1]:
            if item[0] == liq_name + ' ' + liq_taste or item[0] == ras_proizv + ' ' + ras_device_arr[0] + ' ' + ras_device_arr[1] + 'Ом':
                item[1] += user_data[callback.from_user.username][0][0]
                add_state = False
        if add_state:
            if add:
                user_data[callback.from_user.username][1].append(
                    [liq_name + ' ' + liq_taste, user_data[callback.from_user.username][0][0],
                     liquids[liq_mg][liq_name][0][2]]
                )
                text = 'Жидкость добавлена!'
                user_data[callback.from_user.username][0][3] = ''
            else:
                for item in ras[ras_type][ras_proizv]:
                    if item[0] + ' ' + item[1] in ras_device:
                        ras_device_arr = item
                user_data[callback.from_user.username][1].append(
                    [ras_proizv + ' ' + ras_device_arr[0] + ' ' + ras_device_arr[1] + 'Ом',
                     user_data[callback.from_user.username][0][0],
                     ras_device_arr[3]]
                )
                text = 'Расходник добавлен!'
                user_data[callback.from_user.username][0][6] = ''
                user_data[callback.from_user.username][0][7] = ''
        user_data[callback.from_user.username][0][8] = bool
        user_data[callback.from_user.username][0][0] = 1
        await callback.message.edit_text(
            text=f'{text}\nВыбери, что хочешь заказать или просмотри свой заказ:',
            reply_markup=get_main_keyboard().as_markup()
        )
        return

    builder.button(text='🔙Назад', callback_data=CallbackFactory(action='back', value=callback_data.action))
    builder.adjust(1)
    if 'количество' in text:
        builder.adjust(2, 1)
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup()
    )
    await callback.answer()


# удаление
@dp.message(StateDel.choosing_num)
async def num_chosen(message: types.Message, state: FSMContext):
    state_del = True
    text = ""
    items = user_data[message.from_user.username][1]

    if message.text.isnumeric() and int(message.text) in range(1, len(items) + 1):
        for item in items:
            if items.index(item) + 1 == int(message.text):
                items.remove(item)
        text += "Позиция успешно удалена из корзины\n\n"
        await state.set_state()
    else:
        text += "Введенное значение не верное, повторите попытку\n\n"
        state_del = False

    builder = InlineKeyboardBuilder()
    if get_cart(message.from_user.username) != '\nИтого: 0 BYN':
        text += get_cart(message.from_user.username)
        if state_del:
            builder.button(text='Удалить позицию', callback_data=CallbackFactory(action='del'))
        builder.button(text='🔙Назад', callback_data=CallbackFactory(action='back', value='del'))
    else:
        text += 'Корзина пуста!'
        builder.button(text='🔙Назад', callback_data=CallbackFactory(action='back', value='cart'))

    builder.adjust(1)
    await message.delete()
    await bot.edit_message_text(text=text, chat_id=message.chat.id,
                                message_id=user_data[message.from_user.username][0][1],
                                reply_markup=builder.as_markup())


@dp.message()
async def unrecognized(message: types.Message):
    await message.delete()


def get_cart(username):
    res = ''
    price = 0
    for item in user_data[username][1]:
        res += f'{user_data[username][1].index(item) + 1}. {item[0]} - {item[1]}шт - {item[2]} BYN\n'
        price += float('.'.join(item[2].split(','))) * item[1]
    res += f'\nИтого: {price} BYN'
    return res


async def get_res():
    global liquids
    global ras
    while True:
        liquids = get_liquids()
        ras = get_ras()
        await asyncio.sleep(60)


async def main():
    asyncio.create_task(get_res())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())