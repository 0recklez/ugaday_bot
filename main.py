import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from config import Config, load_config

config: Config = load_config()
BOT_TOKEN: str = config.tg_bot.token

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

ATTEMPTS = 7

user = {'in_game': False,
        'secret_number': 0,
        'attempts': 0,
        'total_games': 0,
        'wins': 0,
        'in_game_cube': False}


def get_random_number() -> int:
    return random.randint(1, 100)


@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        'привет!\nсыграем в игру "угадай число"?\n\n'
        'чтобы получить правила игры и список доступных '
        'команд - отправьте команду /help')


@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer('правила игры:\n\nя загадываю число от 1 до 100, '
                         f'а вам нужно его угадать\nу вас есть {ATTEMPTS} '
                         'попыток\n\nдоступные команды:\n/help - правила '
                         'игры и список команд\n/cancel - выйти из игры\n'
                         '/stats - посмотреть статистику\n'
                         '/cube - кинуть кубик\n\n'
                         'ну что сыграем?(напиши да)')


@dp.message(Command(commands='stats'))
async def process_stat_command(message: Message):
    await message.answer(f'в разработке(статистика всех игр в боте) '
                         f'всего игр сыграно: {user["total_games"]}\n'
                         f'побед: {user["wins"]}')


@dp.message(Command(commands='cancel'))
async def process_cancel_command(message: Message):
    if user['in_game']:
        user['in_game'] = False
        await message.answer('вы вышли из игры')
    else:
        await message.answer('вы и так не играете')


@dp.message(Command(commands='cube'))
async def process_cube_answer(message: Message):
    user["in_game_cube"] = True
    await message.answer('попробуй угадать какая цифра выпадет')


@dp.message(F.text.lower().in_(['да', 'давай', 'сыграем', 'игра',
                                'играть', 'хочу играть']))
async def process_positive_answer(message: Message):
    if not user["in_game"]:
        user["in_game"] = True
        user["secret_number"] = get_random_number()
        user["attempts"] = ATTEMPTS
        await message.answer('игра началась!\n'
                             'я загадал число от 1 до 100\n'
                             f'попробуй угадать его за {ATTEMPTS} попыток')
    else:
        await message.answer('игра уже идет')


@dp.message(F.text.lower().in_(['нет', 'не', 'не хочу', 'не буду']))
async def process_negative_answer(message: Message):
    if not user["in_game"]:
        await message.answer('если захотите поиграть просто напишите об этом')
    else:
        await message.answer('сейчас же идет игра, угадайте число')


@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 7 and user["in_game_cube"])
async def process_cube_answer(message: Message):
    msg = await message.answer_dice()
    user["in_game_cube"] = False
    if msg.dice.value == int(message.text):
        user["total_games"] += 1
        user["wins"] += 1
        await message.answer('вы угадали!')
    else:
        await message.answer('вы не угадали(')


@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_number_answer(message: Message):
    if user["in_game"]:
        if int(message.text) == user["secret_number"]:
            user["in_game"] = False
            user["total_games"] += 1
            user["wins"] += 1
            await message.answer("🥳🥳🥳\nвы угадали число, сыграем еще раз?")
        elif int(message.text) > user["secret_number"]:
            user["attempts"] -= 1
            await message.answer('мое число меньше')
        elif int(message.text) < user["secret_number"]:
            user["attempts"] -= 1
            await message.answer('мое число больше')
        if user["attempts"] == 0:
            user["in_game"] = False
            user["total_games"] += 1
            await message.answer('😭😭😭\n'
                                 f'вы проиграли, загаданное число было {user["secret_number"]}\n'
                                 f'сыграем еще раз?')
    else:
        await message.answer("мы еще не играем, хотите сыграть?")


@dp.message()
async def process_other_answers(message: Message):
    if user["in_game"]:
        await message.answer("введите число от 1 до 100")
    else:
        await message.answer('я вас не понимаю\n'
                             'чтобы посмотреть мои команды введите /help')


dp.run_polling(bot)
