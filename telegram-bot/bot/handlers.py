from aiogram import Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
import aiohttp
from backend.models import Application, Coauthor
from bot.states import ApplicationState
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

router = Router()

async def fetch_conferences():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:8000/conferences') as response:
            if response.status == 200:
                conferences = await response.json()
                detailed_conferences = []
                for conf in conferences:
                    detailed_conf = await fetch_conference_details(conf['id'])
                    if detailed_conf:
                        detailed_conferences.append(detailed_conf)
                return detailed_conferences
            else:
                return None

async def fetch_user_applications(telegram_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://127.0.0.1:8000/applications/{telegram_id}') as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

async def fetch_conference_details(conference_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://127.0.0.1:8000/conferences/{conference_id}') as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

async def send_application(conference_id, application_data):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'http://127.0.0.1:8000/conferences/{conference_id}/applications', json=application_data) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

async def edit_application(conference_id, application_id, update_data):
    async with aiohttp.ClientSession() as session:
        async with session.patch(f'http://127.0.0.1:8000/conferences/{conference_id}/applications/{application_id}', json=update_data) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

async def delete_application(conference_id, application_id, delete_data):
    async with aiohttp.ClientSession() as session:
        async with session.delete(f'http://127.0.0.1:8000/conferences/{conference_id}/applications/{application_id}', json=delete_data) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


def format_date(date_str, include_time=False):
    date = datetime.fromisoformat(date_str)
    return date.strftime("%d.%m.%Y %H:%M" if include_time else "%d.%m.%Y")

@router.message(Command('start'))
async def start_cmd(message: types.Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = data.get("telegram_id") or message.from_user.id
    conferences = await fetch_conferences()
    user_applications = await fetch_user_applications(telegram_id)

    if not conferences:
        await message.answer("В данный момент нет доступных конференций для подачи заявок")
        return

    current_time = datetime.now().isoformat()
    inline_kb = InlineKeyboardBuilder()

    for conf in conferences:
        user_applied = user_applications and any(app['conference_id'] == conf['id'] for app in user_applications)
        is_registration_open = conf['application_start'] <= current_time <= conf['application_end']

        button_text = f"{conf['short_name']} - {'Регистрация открыта ✔️' if is_registration_open else 'Регистрация закрыта ✖️'}"
        if user_applied:
            button_text += " (Вы подавали заявку)"

        inline_kb.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f"conference_{conf['id']}"
        ))

    inline_kb.adjust(1)

    await message.answer("Выберите конференцию:", reply_markup=inline_kb.as_markup())

@router.callback_query(F.data.startswith('conference_'))
async def conference_callback(callback_query: types.CallbackQuery, state: FSMContext):
    conference_id = int(callback_query.data.split('_')[1])
    await state.update_data(conference_id=conference_id)
    conference_details = await fetch_conference_details(conference_id)
    if conference_details:
        response = (
            f"Информация о конференции:\n\n"
            f"Полное название: {conference_details['full_name']}\n"
            f"Короткое название: {conference_details['short_name']}\n"
            f"Организация: {conference_details['organization']}\n"
            f"Дата начала: {format_date(conference_details['conference_start'])}\n"
            f"Дата окончания: {format_date(conference_details['conference_end'])}\n"
            f"Подача заявок: {format_date(conference_details['application_start'])} - {format_date(conference_details['application_end'])}\n"
            f"Email организаторов: {conference_details['contact_email']}\n"
            f"Сайт: {conference_details.get('website', 'Не указан')}\n"
        )
        await callback_query.message.answer(response, parse_mode="HTML")
    else:
        await callback_query.message.answer(
            "Не удалось получить информацию о конференции. Пожалуйста, попробуйте еще раз позже"
        )
        return

    telegram_id = callback_query.from_user.id
    user_applications = await fetch_user_applications(telegram_id)
    current_time = datetime.now().isoformat()
    is_registration_open = conference_details['application_start'] <= current_time <= conference_details['application_end']
    registration_not_started = current_time < conference_details['application_start']
    registration_ended = current_time > conference_details['application_end']

    inline_kb = InlineKeyboardBuilder()

    if user_applications:
        applications_for_conference = [app for app in user_applications if app['conference_id'] == conference_id]

        if applications_for_conference:
            response = "Ваши заявки на эту конференцию:\n\n"
            for app in applications_for_conference:
                inline_kb.add(InlineKeyboardButton(
                    text=f"Заявка №{app['id']}",
                    callback_data=f"application_{conference_id}_{app['id']}"
                ))
        else:
            if registration_not_started:
                response = "Подача заявок еще не началась."
            elif registration_ended:
                response = "Срок подачи заявок истек."
            else:
                response = "Вы еще не подали заявку на участие."
    else:
        response = "Не удалось получить ваши заявки. Пожалуйста, попробуйте еще раз позже"

    if is_registration_open:
        inline_kb.add(InlineKeyboardButton(
            text="Подать новую заявку",
            callback_data=f"new_application_{conference_id}"
        ))

    inline_kb.add(InlineKeyboardButton(
        text="Назад",
        callback_data="back_to_conferences"
    ))

    inline_kb.adjust(1)

    await callback_query.message.answer(
        response,
        reply_markup=inline_kb.as_markup()
    )

@router.callback_query(F.data == "back_to_conferences")
async def back_to_conferences(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(telegram_id=str(callback_query.from_user.id))
    await start_cmd(callback_query.message, state)

@router.callback_query(F.data.startswith('application_'))
async def application_details_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data_parts = callback_query.data.split('_')
    conference_id = int(data_parts[1])
    application_id = int(data_parts[2])
    telegram_id = callback_query.from_user.id
    user_applications = await fetch_user_applications(telegram_id)
    conference_details = await fetch_conference_details(conference_id)

    if not user_applications or not conference_details:
        await callback_query.message.answer("Не удалось получить данные. Пожалуйста, попробуйте еще раз позже")
        return

    application = next((app for app in user_applications if app['conference_id'] == conference_id and app['id'] == application_id), None)
    if application:
        await state.update_data(conference_id=application['conference_id'], application_id=application['id'])
        coauthors_str = ", ".join(
            [f"{co['surname']} {co['name']} {co['patronymic']}" for co in application['coauthors']]
        )

        response_parts = [
            f"Заявка №{application['id']}",
            f"Дата подачи: {format_date(application['submitted_at'], include_time=True)}",
            f"Дата обновления: {format_date(application['updated_at'], include_time=True)}",
            f"Email: {application['email']}",
        ]

        if application.get('phone'):
            response_parts.append(f"Телефон: {application['phone']}")
        response_parts.append(f"ФИО: {application['surname']} {application['name']} {application['patronymic']}")
        response_parts.append(f"Университет: {application['university']}")
        if application.get('student_group'):
            response_parts.append(f"Учебная группа: {application['student_group']}")
        response_parts.append(f"Роль: {application['applicant_role']}")
        response_parts.append(f"Название работы: {application['title']}")
        response_parts.append(f"Научный руководитель: {application['adviser']}")
        if coauthors_str:
            response_parts.append(f"Соавторы: {coauthors_str}")

        response = "\n".join(response_parts)

        inline_kb = InlineKeyboardBuilder()

        current_time = datetime.now().isoformat()
        if conference_details['application_start'] <= current_time <= conference_details['application_end']:
            inline_kb.add(InlineKeyboardButton(
                text="Редактировать",
                callback_data=f"edit_application_{application['conference_id']}_{application['id']}"
            ))
            inline_kb.add(InlineKeyboardButton(
                text="Удалить",
                callback_data=f"delete_application_{application['conference_id']}_{application['id']}"
            ))

        inline_kb.add(InlineKeyboardButton(
            text="Назад",
            callback_data=f"conference_{application['conference_id']}"
        ))
        inline_kb.adjust(1)

        await callback_query.message.answer(response[:4096], parse_mode="HTML", reply_markup=inline_kb.as_markup())
    else:
        await callback_query.message.answer("Не удалось найти заявку. Пожалуйста, попробуйте еще раз позже")



@router.callback_query(F.data.startswith('delete_application_'))
async def delete_application_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data_parts = callback_query.data.split('_')
    conference_id = int(data_parts[2])
    application_id = int(data_parts[3])
    telegram_id = callback_query.from_user.id

    delete_data = {
        "telegram_id": str(telegram_id)
    }

    response = await delete_application(conference_id, application_id, delete_data)
    if response:
        await callback_query.message.answer(response["message"])
    else:
        await callback_query.message.answer("Произошла ошибка при удалении заявки. Пожалуйста, попробуйте еще раз позже")

    await return_to_conference(callback_query.message, conference_id, telegram_id)



@router.callback_query(F.data.startswith('edit_application_'))
async def edit_application_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data_parts = callback_query.data.split('_')
    conference_id = int(data_parts[2])
    application_id = int(data_parts[3])
    telegram_id = callback_query.from_user.id
    user_applications = await fetch_user_applications(telegram_id)
    application = next((app for app in user_applications if app['conference_id'] == conference_id and app['id'] == application_id), None)
    if application:
        await state.update_data(
            conference_id=conference_id,
            application_id=application_id,
            telegram_id=str(telegram_id),
            discord_id=application['discord_id'],
            email=application['email'],
            phone=application['phone'],
            name=application['name'],
            surname=application['surname'],
            patronymic=application['patronymic'],
            university=application['university'],
            student_group=application['student_group'],
            applicant_role=application['applicant_role'],
            title=application['title'],
            adviser=application['adviser'],
            coauthors=application['coauthors']
        )
        await callback_query.message.answer("Введите Ваш Discord ID:", reply_markup=skip_exit_keyboard())
        await state.set_state(ApplicationState.waiting_for_discord_id)
    else:
        await callback_query.message.answer("Не удалось найти заявку для редактирования. Пожалуйста, попробуйте еще раз позже")

def skip_exit_keyboard(optional=True):
    buttons = [types.KeyboardButton(text="Выйти")]
    if optional:
        buttons.insert(0, types.KeyboardButton(text="Пропустить"))
    return types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[buttons])

async def return_to_conference(callback_query_or_message, conference_id, telegram_id):
    conference_details = await fetch_conference_details(conference_id)
    user_applications = await fetch_user_applications(telegram_id)

    if not conference_details:
        await callback_query_or_message.answer("Не удалось получить информацию о конференции. Пожалуйста, попробуйте еще раз позже")
        return

    conference_info = (
        f"Информация о конференции:\n\n"
        f"Полное название: {conference_details['full_name']}\n"
        f"Короткое название: {conference_details['short_name']}\n"
        f"Организация: {conference_details['organization']}\n"
        f"Дата начала: {format_date(conference_details['conference_start'])}\n"
        f"Дата окончания: {format_date(conference_details['conference_end'])}\n"
        f"Подача заявок: {format_date(conference_details['application_start'])} - {format_date(conference_details['application_end'])}\n"
        f"Email организаторов: {conference_details['contact_email']}\n"
        f"Сайт: {conference_details.get('website', 'Не указан')}\n"
    )
    await callback_query_or_message.answer(conference_info, parse_mode="HTML")

    current_time = datetime.now().isoformat()
    is_registration_open = conference_details['application_start'] <= current_time <= conference_details['application_end']
    registration_not_started = current_time < conference_details['application_start']
    registration_ended = current_time > conference_details['application_end']

    inline_kb = InlineKeyboardBuilder()

    if user_applications:
        applications_for_conference = [app for app in user_applications if app['conference_id'] == conference_id]

        if applications_for_conference:
            response = "Ваши заявки на эту конференцию:\n\n"
            for app in applications_for_conference:
                inline_kb.add(InlineKeyboardButton(
                    text=f"Заявка №{app['id']}",
                    callback_data=f"application_{conference_id}_{app['id']}"
                ))
        else:
            if registration_not_started:
                response = "Подача заявок еще не началась."
            elif registration_ended:
                response = "Срок подачи заявок истек."
            else:
                response = "Вы еще не подали заявку на участие."
    else:
        response = "Не удалось получить ваши заявки. Пожалуйста, попробуйте еще раз позже"

    if is_registration_open:
        inline_kb.add(InlineKeyboardButton(
            text="Подать новую заявку",
            callback_data=f"new_application_{conference_id}"
        ))

    inline_kb.add(InlineKeyboardButton(
        text="Назад",
        callback_data="back_to_conferences"
    ))

    inline_kb.adjust(1)

    await callback_query_or_message.answer(
        response,
        reply_markup=inline_kb.as_markup()
    )

@router.callback_query(F.data.startswith('new_application_'))
async def new_application_callback(callback_query: types.CallbackQuery, state: FSMContext):
    conference_id = int(callback_query.data.split('_')[2])
    telegram_id = callback_query.from_user.id

    await state.update_data(conference_id=conference_id, telegram_id=str(telegram_id))

    await callback_query.message.answer("Введите Ваш Discord ID:", reply_markup=skip_exit_keyboard())
    await state.set_state(ApplicationState.waiting_for_discord_id)

@router.message(Command('new_application'))
async def new_application_message(message: types.Message, state: FSMContext):
    conference_id = int(message.text.split("_")[1])
    conference_details = await fetch_conference_details(conference_id)
    if not conference_details:
        await message.answer("Не удалось получить информацию о конференции. Пожалуйста, попробуйте еще раз позже")
        return
    current_time = datetime.now().isoformat()
    if not (conference_details['application_start'] <= current_time <= conference_details['application_end']):
        await message.answer("Регистрация на эту конференцию закрыта")
        return
    telegram_id = message.from_user.id

    await state.update_data(conference_id=conference_id, telegram_id=str(telegram_id))
    await message.answer("Введите Ваш Discord ID:", reply_markup=skip_exit_keyboard())
    await state.set_state(ApplicationState.waiting_for_discord_id)

@router.message(ApplicationState.waiting_for_discord_id)
async def process_discord_id(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conference_id = data.get("conference_id")
    telegram_id = message.from_user.id

    if message.text.lower() == "выйти":
        await state.clear()
        await message.answer("Процесс отменен", reply_markup=types.ReplyKeyboardRemove())
        await return_to_conference(message, conference_id, telegram_id)
        return

    if message.text.lower() != "пропустить":
        await state.update_data(discord_id=message.text)
    else:
        await state.update_data(discord_id=None)

    await message.answer("Введите Ваш EMAIL:", reply_markup=skip_exit_keyboard(optional=False))
    await state.set_state(ApplicationState.waiting_for_email)

@router.message(ApplicationState.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conference_id = data.get("conference_id")
    telegram_id = message.from_user.id

    if message.text.lower() == "выйти":
        await state.clear()
        await message.answer("Процесс отменен", reply_markup=types.ReplyKeyboardRemove())
        await return_to_conference(message, conference_id, telegram_id)
        return

    if "@" in message.text:
        await state.update_data(email=message.text)
        await message.answer("Введите Ваш номер телефона:", reply_markup=skip_exit_keyboard())
        await state.set_state(ApplicationState.waiting_for_phone)
    else:
        await message.answer("Введите корректный EMAIL")

@router.message(ApplicationState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conference_id = data.get("conference_id")
    telegram_id = message.from_user.id

    if message.text.lower() == "выйти":
        await state.clear()
        await message.answer("Процесс отменен", reply_markup=types.ReplyKeyboardRemove())
        await return_to_conference(message, conference_id, telegram_id)
        return

    if message.text.lower() != "пропустить":
        await state.update_data(phone=message.text)

    await message.answer("Введите Ваше ФИО (в формате 'Фамилия Имя Отчество'):", reply_markup=skip_exit_keyboard(optional=False))
    await state.set_state(ApplicationState.waiting_for_full_name)

@router.message(ApplicationState.waiting_for_full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conference_id = data.get("conference_id")
    telegram_id = message.from_user.id

    if message.text.lower() == "выйти":
        await state.clear()
        await message.answer("Процесс отменен", reply_markup=types.ReplyKeyboardRemove())
        await return_to_conference(message, conference_id, telegram_id)
        return

    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Введите корректное ФИО (в формате 'Фамилия Имя Отчество')")
        return

    surname, name, patronymic = parts
    await state.update_data(name=name, surname=surname, patronymic=patronymic)

    await message.answer("Введите Ваш университет:", reply_markup=skip_exit_keyboard(optional=False))
    await state.set_state(ApplicationState.waiting_for_university)

@router.message(ApplicationState.waiting_for_university)
async def process_university(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conference_id = data.get("conference_id")
    telegram_id = message.from_user.id

    if message.text.lower() == "выйти":
        await state.clear()
        await message.answer("Процесс отменен", reply_markup=types.ReplyKeyboardRemove())
        await return_to_conference(message, conference_id, telegram_id)
        return

    if message.text.lower() != "пропустить":
        await state.update_data(university=message.text)

    await message.answer("Введите Вашу учебную группу:", reply_markup=skip_exit_keyboard())
    await state.set_state(ApplicationState.waiting_for_student_group)

@router.message(ApplicationState.waiting_for_student_group)
async def process_student_group(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conference_id = data.get("conference_id")
    telegram_id = message.from_user.id

    if message.text.lower() == "выйти":
        await state.clear()
        await message.answer("Процесс отменен", reply_markup=types.ReplyKeyboardRemove())
        await return_to_conference(message, conference_id, telegram_id)
        return

    if message.text.lower() != "пропустить":
        await state.update_data(student_group=message.text)

    await message.answer("Введите Вашу роль (студент, аспирант и т.д.):", reply_markup=skip_exit_keyboard(optional=False))
    await state.set_state(ApplicationState.waiting_for_applicant_role)

@router.message(ApplicationState.waiting_for_applicant_role)
async def process_applicant_role(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conference_id = data.get("conference_id")
    telegram_id = message.from_user.id

    if message.text.lower() == "выйти":
        await state.clear()
        await message.answer("Процесс отменен", reply_markup=types.ReplyKeyboardRemove())
        await return_to_conference(message, conference_id, telegram_id)
        return

    if message.text.lower() != "пропустить":
        await state.update_data(applicant_role=message.text)

    await message.answer("Введите название Вашей работы:", reply_markup=skip_exit_keyboard(optional=False))
    await state.set_state(ApplicationState.waiting_for_title)

@router.message(ApplicationState.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conference_id = data.get("conference_id")
    telegram_id = message.from_user.id

    if message.text.lower() == "выйти":
        await state.clear()
        await message.answer("Процесс отменен", reply_markup=types.ReplyKeyboardRemove())
        await return_to_conference(message, conference_id, telegram_id)
        return

    if message.text.lower() != "пропустить":
        await state.update_data(title=message.text)

    await message.answer("Введите ФИО Вашего научного руководителя (в формате 'Фамилия Имя Отчество'):", reply_markup=skip_exit_keyboard(optional=False))
    await state.set_state(ApplicationState.waiting_for_adviser)

@router.message(ApplicationState.waiting_for_adviser)
async def process_adviser(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conference_id = data.get("conference_id")
    telegram_id = message.from_user.id

    if message.text.lower() == "выйти":
        await state.clear()
        await message.answer("Процесс отменен", reply_markup=types.ReplyKeyboardRemove())
        await return_to_conference(message, conference_id, telegram_id)
        return

    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Введите корректное ФИО (в формате 'Фамилия Имя Отчество', разделяя их запятыми)")
        return

    adviser_surname, adviser_name, adviser_patronymic = parts
    await state.update_data(adviser=f"{adviser_surname} {adviser_name} {adviser_patronymic}")

    await message.answer("Введите соавторов (в формате 'Фамилия Имя Отчество'):", reply_markup=skip_exit_keyboard())
    await state.set_state(ApplicationState.waiting_for_coauthors)

@router.message(ApplicationState.waiting_for_coauthors)
async def process_coauthors(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conference_id = data.get("conference_id")
    telegram_id = message.from_user.id

    if message.text.lower() == "выйти":
        await state.clear()
        await message.answer("Процесс отменен", reply_markup=types.ReplyKeyboardRemove())
        await return_to_conference(message, conference_id, telegram_id)
        return

    coauthors_input = message.text
    coauthors_list = []
    if coauthors_input.lower() != "пропустить":
        coauthors = coauthors_input.split(",")
        for coauthor in coauthors:
            parts = coauthor.strip().split(" ")
            if len(parts) == 3:
                coauthors_list.append(Coauthor(
                    name=parts[1],
                    surname=parts[0],
                    patronymic=parts[2]
                ))
            else:
                await message.answer("Введите корректное ФИО соавторов (в формате 'Фамилия Имя Отчество', разделяя их запятыми)")
                return

    data = await state.get_data()
    conference_id = data.get("conference_id")
    application_id = data.get("application_id")

    application_data = Application(
        telegram_id=data.get("telegram_id"),
        discord_id=data.get("discord_id"),
        email=data.get("email"),
        phone=data.get("phone"),
        name=data.get("name"),
        surname=data.get("surname"),
        patronymic=data.get("patronymic"),
        university=data.get("university"),
        student_group=data.get("student_group"),
        applicant_role=data.get("applicant_role"),
        title=data.get("title"),
        adviser=data.get("adviser"),
        coauthors=coauthors_list
    ).dict()

    if application_id:
        updated_application = await edit_application(conference_id, application_id, application_data)
    else:
        updated_application = await send_application(conference_id, application_data)

    if updated_application:
        coauthors_str = ", ".join(
            [f"{co['surname']} {co['name']} {co['patronymic']}" for co in updated_application.get('coauthors', [])]
        )

        response_parts = [
            f"Ваша заявка была успешно {'обновлена' if application_id else 'отправлена'}!",
            f"Дата подачи: {format_date(updated_application.get('submitted_at'), include_time=True)}",
            f"Дата обновления: {format_date(updated_application.get('updated_at'), include_time=True)}",
            f"Email: {updated_application.get('email')}",
        ]

        if updated_application.get('phone'):
            response_parts.append(f"Телефон: {updated_application.get('phone')}")
        response_parts.append(f"ФИО: {updated_application.get('surname')} {updated_application.get('name')} {updated_application.get('patronymic')}")
        response_parts.append(f"Университет: {updated_application.get('university')}")
        if updated_application.get('student_group'):
            response_parts.append(f"Учебная группа: {updated_application.get('student_group')}")
        response_parts.append(f"Роль: {updated_application.get('applicant_role')}")
        response_parts.append(f"Название работы: {updated_application.get('title')}")
        response_parts.append(f"Научный руководитель: {updated_application.get('adviser')}")
        if coauthors_str:
            response_parts.append(f"Соавторы: {coauthors_str}")

        response = "\n".join(response_parts)

        await message.answer(response, parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove())
        await return_to_conference(message, conference_id, telegram_id)
    else:
        await message.answer(f"Произошла ошибка при {'обновлении' if application_id else 'отправке'} заявки. Пожалуйста, попробуйте еще раз позже", reply_markup=types.ReplyKeyboardRemove())

    await state.clear()


def register_handlers(dp: Dispatcher):
    dp.include_router(router)
