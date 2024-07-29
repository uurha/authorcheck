import asyncio
import logging
import sys
import configparser
import csv
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery


add = InlineKeyboardButton(text='Додати русню', callback_data='add')
link = InlineKeyboardButton(text='Автор бота', url='t.me/kimino_musli')
kb_start = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[[link], [add]])

cfg = configparser.ConfigParser()
cfg.read('cfg.ini')

bot = Bot(token=os.environ.get('TOKEN'), parse_mode='HTML')
dp = Dispatcher()

ids = cfg['EDITORS']['id']
editors = [int(num.strip()) for num in ids.split(',')]


async def author_add(name, info):
    with open('db.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow([name, info])
    print('db updated')
    csvfile.close()


async def author_check(search_name):
    try:
        results = []
        with open('db.csv', 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                if len(row) == 2:
                    name, info = row
                    possible_values = name.split(' ')
                    if search_name in possible_values:
                        results.append((name, info))
        csvfile.close()
        return results if results else None
    except FileNotFoundError:
        print('DB not found or corrupted')
        return None, None


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer(
        'Хочеш перевірити, чи автор є руснею?\nПросто введи:\n\n<b><i>!c *нікнейм*</i></b>'
        '\n\n\n<u><i>всі команди мають писатися латинськими літерами</i></u>', reply_markup=kb_start)


@dp.message(Command('c', prefix='!'))
async def send_check_result(message: types.Message, command: CommandObject):
    print(f'Check request: {command.args}')

    if command.args is None:
        await message.reply('Команду введено неправильно. Ось приклад:\n\n!с *nickname*')
    else:
        search = await author_check(command.args)
        if search:
            formatted_msg = '\n'.join(f'Обережно! <b>{name}</b> є небаженим(ою) до поширення.\nПричина:\n\n<u>{info}</u>' for name, info in search)
            await message.reply(formatted_msg)
        else:
            await message.reply('На щастя - нічого не знайдено!\nАле радимо додатково перевіряти авторів')


@dp.message(Command('a', prefix='!'))
async def send_add_russian(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    if user_id in editors:
        print(f'Adding: {command.args} by {user_id}')
        if command.args is None:
            await message.reply('Будь ласка, введіть команду `!a` та два рядки, розділені '
                                'натисканням клавіші Shift+Enter.')
        else:
            lines = command.args.split('\n')
            if len(lines) == 2:
                name, info = lines[0], lines[1]
                await author_add(name, info)
                await message.reply(f'Успішно внесено до русні:\n\nНікнейм: {name}\nПричина: {info}')
            else:
                await message.reply('Будь ласка, введіть команду `!a` та два рядки, розділені '
                                    'натисканням клавіші Enter.')
    else:
        await message.reply('Нажаль, ви не маєте доступу до виконання даної команди. ')


@dp.callback_query(lambda c: c.data == 'add')
async def add(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        'В боті є можливість поповнювати базу руснявих авторів використовуючи команду:\n\n'
        '<i>!a *нікнейм_и*\n</i>'
        '<i>*причина руснявості*</i>\n\n'
        'Дана функція доступна лише деяким довіреним особам з міркувань безпеки. '
        'Тому якщо ви не є у цьому списку, але бажаєте доповнити базу - звертайтесь до мене, '
        '<a href="t.me/kimino_musli">KimiNo</a>'
    )


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
