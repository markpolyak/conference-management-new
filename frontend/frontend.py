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
from aiogram.types import Message, KeyboardButton, FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import cfg
from utils import download_file, fetch

bot = Bot(token=cfg.ORG_BOT, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

class Reg(StatesGroup):
    name = State()
    status = State()
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

def is_valid_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except ValueError:
        return False
    
def is_bigger_than_current_date(date_str: str) -> bool:
    current_date = datetime.now().date()
    input_date = datetime.strptime(date_str, "%d.%m.%Y").date()
    if(current_date <= input_date):
        return True
    else:
        return False
    
def is_valid_time(time_str: str) -> bool:
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False
    
def is_bigger_than_current_time(date_str: str, time_str: str) -> bool:
    try:
        input_datetime = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
        current_datetime = datetime.now()
        return input_datetime > current_datetime
    except ValueError:
        return False


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:

    response = await fetch("GET", "/getOrgName", {'telegramId': message.from_user.id})

    if(response):

        sheet_id = (await fetch("GET", "/getSheetId", params={"telegramId": message.from_user.id}))["message"]

        if(not sheet_id):
            sheet_id = (await fetch("POST", "/createOrganizator", data={"telegramId": message.from_user.id, "email": cfg.ACCESS_EMAIL}))["message"]

        await message.answer(f"Организатор. Добрый вечер {response["org_name"]}\n Ваша уникальная ссылка для конференций: {sheet_id}")
        
        keyboard = ReplyKeyboardBuilder()
        keyboard.row(
            KeyboardButton(text="Добавить конференцию"),
            KeyboardButton(text="Изменить конференцию")
        )
        keyboard.row(
            KeyboardButton(text="Список моих конференций"),
            KeyboardButton(text="Создать уведомление")
        )
        keyboard.row(
            KeyboardButton(text="Cкачать список заявок по форме"),
        )
        keyboard.row(
            KeyboardButton(text="Скачать отчет о проведении конференции"),
        )
        keyboard.row(
            KeyboardButton(text="скачать список докладов, представляемых к публикации"),
        )

        await message.answer("Выберите:", reply_markup=keyboard.as_markup(resize_keyboard=True))

    else:
        await message.answer(f"Вы не ялвяетесь организатором конференций")

# ОБРАБОТКА КНОПОК
@dp.message(F.text == "Добавить конференцию")
async def organization_handler(message: Message, state: FSMContext):
    await message.answer(f"Введите название конференции")
    await state.set_state(Reg.conference_name)

@dp.message(Reg.conference_name)
async def add_conference_name_handler(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer(f"Введите дату проведения конференции")
    await state.set_state(Reg.conference_date)

@dp.message(Reg.conference_date)
async def add_conference_date_handler(message: Message, state: FSMContext):
    date = message.text

    if(is_valid_date(date)):

        if(is_bigger_than_current_date(date)):
            await state.update_data(conference_date=date)
            await message.answer(f"Введите время проведения конференции")
            await state.set_state(Reg.conference_time)
        else:
            await message.answer("Неправильный ввод. Указанная дата меньше текущей")

    else:
        await message.answer("Неправильный ввод. Введите дату в формате DD:MM:YYYY. Например 8.07.2024")    

@dp.message(Reg.conference_time)
async def add_conference_time_handler(message: Message, state: FSMContext):
    time = message.text

    if(is_valid_time(time)):
        states = await state.get_data()
        if(is_bigger_than_current_time(states["conference_date"], time)):
            await state.update_data(conference_time=time)
            try:
                response = await fetch("POST", "/addConference", data={"telegramId": message.from_user.id, "theme": states["name"], "time": {"day": states["conference_date"], "time": time}})
                await message.answer(f"Конференция создана. \nНазвание: {states["name"]}\nДата и время: {states["conference_date"]} {time}\n\nУникальный идентификатор: {response['message']}")
            except Exception as e:
                await message.answer(str(e))
            await state.clear()
        else:
            await message.answer("Неправильный ввод. Указанное время меньше текущего")

    else:
        await message.answer("Неправильный ввод. Введите время в формате HH:MM. Например 18:10")

@dp.message(F.text == "Изменить конференцию")
async def organization_handler(message: Message, state: FSMContext):
    await message.answer(f"Введите Id конференции")
    await state.set_state(Reg.change_conf_id)

@dp.message(Reg.change_conf_id)
async def change_conf_theme_handler(message: Message, state: FSMContext):
    confId = message.text
    
    rawData = (await fetch("GET", "/getAllConferenceData", params={"telegramId": message.from_user.id}))["response"][1:]

    for row in rawData:
        if confId in row:
            await state.update_data(change_conf_id=confId)
            await message.answer(f"Введите новое название конференции")
            await state.set_state(Reg.change_conf_theme)
            return
            
    message.answer(f"Конференции {confId} не существует")

@dp.message(Reg.change_conf_theme)
async def change_conf_theme_handler(message: Message, state: FSMContext):
    theme = message.text
    await state.update_data(change_conf_theme=theme)
    await message.answer(f"Введите новую дату проведения конференции")
    await state.set_state(Reg.change_conf_day)

@dp.message(Reg.change_conf_day)
async def change_conf_day_handler(message: Message, state: FSMContext):
    date = message.text
        
    if(is_valid_date(date)):

        if(is_bigger_than_current_date(date)):
            await state.update_data(change_conf_day=date)
            await message.answer(f"Введите новое время проведения конференции")
            await state.set_state(Reg.change_conf_time)
        else:
            await message.answer("Неправильный ввод. Указанная дата меньше текущей")

    else:
        await message.answer("Неправильный ввод. Введите дату в формате DD:MM:YYYY. Например 8.07.2024")   

@dp.message(Reg.change_conf_time)
async def change_conf_day_handler(message: Message, state: FSMContext):
    time = message.text
    await state.update_data(change_conf_time=time)
    
    states = await state.get_data()
    
    if(is_valid_time(time)):
        states = await state.get_data()
        if(is_bigger_than_current_time(states["change_conf_day"], time)):
            await state.update_data(conference_time=time)
            
            try:
                response = await fetch("POST", "/updateConference", data={"telegramId": message.from_user.id, "conferenceId": states["change_conf_id"], "theme": states["change_conf_theme"], "time": {"day": states["change_conf_day"], "time": states["change_conf_time"]}})
                await message.answer(f"Данные успешно изменены")
                await message.answer(f"Название: {states["change_conf_theme"]}\nДата и время: {states["change_conf_day"]} {states["change_conf_time"]}")
                await state.clear()
            except Exception as e:
                await state.clear()
                raise e
            
        else:
            await message.answer("Неправильный ввод. Указанное время меньше текущего")
    
    else:
        await message.answer("Неправильный ввод. Введите время в формате HH:MM. Например 18:10")
        
    

@dp.message(F.text == "Список моих конференций")
async def my_all_conf_handler(message: Message, state: FSMContext):
    response = await fetch("GET", "/getAllOrgConferenceWithData", params={"telegramId": message.from_user.id})
    allConference = response["response"][1:]
    
    if(len(allConference) > 0):
        formatted_data = []
        for conference in allConference:
            conference_id = conference[0]
            conference_name = conference[1]
            conference_date = ast.literal_eval(conference[2])
            conference_participants = ast.literal_eval(conference[3])
            
            formatted_string = (f"Id конференции: {conference_id}\n"
                                f"Название конференции: {conference_name}\n"
                                f"Дата: {conference_date['day']} {conference_date['time']}\n"
                                f"Количество участников: {len(conference_participants)}\n")
            
            formatted_data.append(formatted_string)

        # Объединение всех строк в одну
        result = "\n".join(formatted_data)
        await message.answer(result)
    else:
        await message.answer("У вас нет созданных конференций")

@dp.message(F.text == "Создать уведомление")
async def create_alert_handler(message: Message, state: FSMContext):
    await message.answer(f"Укажите id конференции")
    await state.set_state(Reg.alert_conf_id)

@dp.message(Reg.alert_conf_id)
async def alert_conf_id(message: Message, state: FSMContext):
    confId = message.text
    
    await state.update_data(alert_conf_id=confId)
    await message.answer(f"Введите текст уведомления")
    await state.set_state(Reg.alert_text)

@dp.message(Reg.alert_text)
async def alert_text(message: Message, state: FSMContext):

    alert_text = message.text
    alert_conf_id = (await state.get_data())["alert_conf_id"]
    
    try:
        response = await fetch("GET", "/getAllConferenceData", params={"telegramId": message.from_user.id})
        rawData = response["response"]
        
        for conf in rawData:
        
            if str(alert_conf_id) in conf:
                
                conference_date = ast.literal_eval(conf[2])
                conference_participants = ast.literal_eval(conf[3])
                participants_count = len(conference_participants)
                
                for participantId in conference_participants:
                    formatted_string = (f"🔔Новое уведомление\n\n"
                                    f"<b>{alert_text}</b>\n\n"
                                    f"Id конференции: {alert_conf_id}\n"
                                    f"Дата: {conference_date['day']} {conference_date['time']}\n"
                                    f"Участников: {participants_count}\n")
                    
                    await fetch(method="POST", path="/sendAlerts", data={"message": formatted_string, "userId": participantId})

                await message.answer("Уведомления отправлены")
                await state.clear()
                return
                
        await message.answer(f"Конференции {alert_conf_id} не найдено")
    
    except Exception as e:
        raise e
    
@dp.message(F.text == "Cкачать список заявок по форме")
async def getApplicationDocx(message: Message, state: FSMContext):
    file_path = "application.docx"
    await download_file("application.docx", "/getApplicationDocx")
    await message.reply_document(FSInputFile(path=file_path))    
    os.remove(file_path)  # Удалить файл после отправки
    
@dp.message(F.text == "Скачать отчет о проведении конференции")
async def getConferenceReportDocx(message: Message, state: FSMContext):
    file_path = "report.docx"
    await download_file("report.docx", "/getConferenceReportDocx")
    await message.reply_document(FSInputFile(path=file_path))    
    os.remove(file_path)  # Удалить файл после отправки
    
@dp.message(F.text == "скачать список докладов, представляемых к публикации")
async def getSubbmittedRepostsDocx(message: Message, state: FSMContext):
    file_path = "submittedReposts.docx"
    await download_file("submittedReposts.docx", "/getSubbmittedRepostsDocx")
    await message.reply_document(FSInputFile(path=file_path))    
    os.remove(file_path)  # Удалить файл после отправки

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())