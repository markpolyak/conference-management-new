import ast
import asyncio
from datetime import datetime
import logging
import os
import sys

from aiogram import F, Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import aiohttp
from typing import Dict, Literal, TypedDict
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import cfg
from utils import fetch

bot = Bot(token=cfg.USER_BOT)
dp = Dispatcher()

class Reg(StatesGroup):
    name = State()
    status = State() #user || organization
    organization = State()
    user = State()

    conference_name = State()
    conference_date = State()
    conference_time = State()

    delete_conf_name = State()

    change_conf_id = State()
    change_conf_theme = State()
    change_conf_day = State()
    change_conf_time = State()

    user_join_to_conf = State()

    alert_conf_id = State()
    alert_text = State()

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    response = await fetch("GET", "/getUserName", {'telegramId': message.from_user.id})

    if(response):

        keyboard = ReplyKeyboardBuilder()
        keyboard.row(
            KeyboardButton(text="Учавствовать в конференции"),
        )

        await message.answer(f"Пользователь. Добрый вечер {response["user_name"]}", reply_markup=keyboard.as_markup(resize_keyboard=True))

    else:
        await message.answer(f"Данных не найдено. Введите имя чтобы зарегистрироваться")
        await state.set_state(Reg.name)

@dp.message(Reg.name)
async def state_name_handler(message: Message, state: FSMContext):
    name = message.text
    chatId = message.chat.id

    keyboard = ReplyKeyboardBuilder()
    keyboard.row(
        KeyboardButton(text="Учавствовать в конференции"),
    )

    await fetch("POST", "/addUser", data={"telegramId": message.from_user.id, "name": name, "chatId": chatId})
    await message.answer(f"Вы зарегистрированы под именем {name}", reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.update_data(status="user")
    await state.clear()

@dp.message(F.text == "Учавствовать в конференции")
async def add_user_to_conference(message: Message, state: FSMContext):
    await message.answer(f"Введите id конференции")
    await state.set_state(Reg.user_join_to_conf)

@dp.message(Reg.user_join_to_conf)
async def change_conf_day_handler(message: Message, state: FSMContext):
    confId = message.text
    
    try:
        response = await fetch("POST", "/addUserToConference", data={"telegramId": message.from_user.id, "conferenceId": confId})
        await message.answer(f"Вы вступили в конференцию {confId}")
    except Exception as e:
        await message.answer(str(e))
    
    await state.clear()


async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())