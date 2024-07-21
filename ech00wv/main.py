import time
import telebot
import re

from config.config import TOKEN
from keyboards.keyboards import *  # функции вывода различных клавиатур
from backend.backend_requests import * # функции обращения к бэку
from secondary_functions.secondary_functions import *  # различные вспомогательные функции, либо функции эмуляции бэкенда


bot = telebot.TeleBot(TOKEN, threaded=False)

users = {} # словарь с ключом chat_id, нужен для хранения пользователей
conferences = [] # массив для хранения событий, будет заполняться при запросе к бэкенду
articles = {} # Словарь со статьями, ключ - application_id TODO: эмуляция


class User:
    def __init__(self):
        # два этих поля используются совместно и позволяют получать нужную встречу и конференцию
        self.conference_index = 0 # индексация конференций, необходима для получения конкретной конференции
        self.application_index = 0 # индексация заявок, необходима для получения конкретной заявки у конкретной конференции

        self.applications = {}  # словарь, ключ - id конференции, значение - список тел заявок

    def add_conference(self, conference_id, application):  # добавление записи на конференцию
        self.applications.setdefault(conference_id, []).append(application)


def get_conferences_list(message): #получить с бэка список конференций

    # TODO: бэкенд
    # active_conferences = fetch_all_conferences('active')
    # filtered_past_conferences = fetch_past_conferences_with_applications(message)
    ###############################
    
    # TODO: эмуляция
    active_conferences = fetch_all_conferences_test('active') # конференции, на которые ведется прием заявок\
    past_conferences = fetch_all_conferences_test('past') # конференции, прием заявок по которым уже прошел
    filtered_past_conferences = [conf for conf in past_conferences if conf['id'] in users[message.chat.id].applications] # фильтрация прошедших конференций по тем, на которые подавал заявки пользователь (для работы с бэком есть отдельная функция)
    ####################################
    
    conferences_list = filtered_past_conferences + active_conferences
    for conference in conferences_list:
        add_status_to_conference(conference) # добавление словаря со статусом для каждого из событий (заявка, статья, конференция)
    return conferences_list


def save_new_application(message, new_application): # сохранить новую заявку
    conference_index = users[message.chat.id].conference_index
    conference = conferences[conference_index]
    conference_id = conference.get('id')
    users[message.chat.id].add_conference(conference_id, new_application)


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in users:
        users[message.chat.id] = User() # создание нового пользователя, если его еще нет
    message = bot.send_message(message.chat.id, '.') # это сообщение обновится
    get_conferences(message)


def get_conferences(message):  # вывод информации о событиях и кнопок управления
    global conferences

    conferences = get_conferences_list(message) # записать в глобальную переменную список конференций с бэка
    if not conferences:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                              text='На данный момент конференции не проводятся, заявок от пользователя нет')
        return
    conference_index = users[message.chat.id].conference_index  # получение индекса от конкретного пользователя

    # условия внизу позволяют отрисовывать только нужные кнопки навигации

    # если присутствует только одна конференция
    if len(conferences) == 1:
        display_brief_conference_info(message)
    # если выбрана первая конференция (не нужно отображать кнопку выбора предыдущей конференции)
    elif conference_index == 0:
        display_brief_conference_info(message, conference_index, 'first')
    # если выбрана последняя конференция (не нужно отображать кнопку выбора следующей конференции)
    elif conference_index == len(conferences) - 1:
        display_brief_conference_info(message, conference_index, 'last')
    # если выбрана конференция из середины списка
    else:
        display_brief_conference_info(message, conference_index, 'mid')


def display_brief_conference_info(message, conference_index=0, position='single'): # вывести краткую информацию о конференции
    conference = conferences[conference_index] # получение нужной конференции и отображение информации по ней
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                          text=f'Название(рус): {conference.get("name_rus_short")}\n'
                               f'Название(англ): {conference.get("name_eng_short")}\n'
                               f'Дата начала: {conference.get("conf_start_date")}\n'
                               f'Дата окончания: {conference.get("conf_end_date")}\n\n'
                               f'{"На данную конференцию ведется прием заявок" if conference.get("status").get("application_status") == "is_opened" else "Прием заявок закрыт, но у пользователя присутствуют заявки на конференцию"}\n'
                               f'{"К данной конференции можно прикрепить статью" if conference.get("status").get("article_status") == "is_opened" else "Прикрепление статей к заявкам на данную конференцию закрыто"}',
                          reply_markup=create_conferences_markup(position))
   
    
def display_detailed_conference_info(message): # вывод подробной информации о конференции
    conference_index = users[message.chat.id].conference_index # получение индекса выбранной конференции

    # TODO: бэкенд
    # conference = fetch_conference_by_id(conferences[conference_index].get('id'))
    #############################

    # TODO: эмуляция
    conference = fetch_conference_by_id_test(conferences[conference_index].get('id')) # получение подробной информации по нужной конференции
    ###############

    conference = add_status_to_conference(conference)
    # получение различных статусов для отображения их в сообщении
    application_status = conference.get('status').get('application_status')
    article_status = conference.get('status').get('article_status')
    conference_status = conference.get('status').get('conference_status')

    # отображение подробной информации по конференции и кнопок управления
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=f"Название конференции (рус): {conference.get('name_rus')}\n"
                                      f"Краткое название (рус): {conference.get('name_rus_short')}\n"
                                      f"Название конференции (англ): {conference.get('name_eng')}\n"
                                      f"Краткое название (англ): {conference.get('name_eng_short')}\n"
                                      f"Дата начала приема заявок: {conference.get('registration_start_date')}\n"
                                      f"Дата окончания приема заявок: {conference.get('registration_end_date')} {'<b><u>Заявки не принимаются</u></b>' if (application_status == 'still_closed' or application_status == 'already_closed') else ''}\n"
                                      f"Дата начала приема статей: {conference.get('submission_start_date')}\n"
                                      f"Дата окончания приема статей: {conference.get('submission_end_date')} {'<b><u>Прием статей закрыт</u></b>' if (article_status == 'still_closed' or article_status == 'already_closed') else ''}\n"
                                      f"Дата начала конференции: {conference.get('conf_start_date')}\n"
                                      f"Дата окончания конференции: {conference.get('conf_end_date')} {'<b><u>В данный момент конференция не проходит</u></b>' if (conference_status == 'still_closed' or conference_status == 'already_closed') else ''}\n"
                                      f"Организатор: {conference.get('organized_by')}\n"
                                      f"Ссылка: {conference.get('url')}\n"
                                      f"Email: {conference.get('email')}",
                          reply_markup=create_detailed_conference_markup(),
                          parse_mode='HTML')
    
    
def get_applications_for_conference(message): # функция для получения заявок на конференцию

    # получение словаря со статусом конференции (передается в функцию, необходимо для отрисовки только нужных кнопок)
    conference_status = conferences[users[message.chat.id].conference_index].get('status')

    # TODO: бэкенд
    # applications = fetch_applications(message, conference.get('id'))
    #######################################

    # TODO: эмуляция
    applications = get_applications_from_user(message, users, conferences) # получение списка заявок на конференцию
    ###############

    # получаем индекс заявки, необходим для навигации
    application_index = users[message.chat.id].application_index

    # условия ниже необходимы для отрисовки только нужных кнопок

    # если заявок на данную конференцию нет
    if applications is None:
        display_brief_application_info(message, conference_status)
    # если заявка только одна (кнопки навигации не нужны)
    elif len(applications) == 1:
        display_brief_application_info(message, conference_status, applications, application_index,  'single')
    # если выбран первый элемент (кнопка "назад" не нужна)
    elif application_index == 0:
        display_brief_application_info(message, conference_status, applications, application_index, 'first')
    # если выбран последний элемент (кнопка "вперед" не нужна)
    elif application_index == len(applications) - 1:
        display_brief_application_info(message, conference_status, applications, application_index, 'last')
    # если выбран элемент из центра
    else:
        display_brief_application_info(message, conference_status, applications, application_index, 'mid')


# функция для отображения краткой информации по заявке и кнопок управления
def display_brief_application_info(message, conference_status='none', applications=None, application_index=0, position='none'):
    if position == 'none': # если заявок нет
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                              text='На данную конференцию не было подано ни одной заявки',
                              reply_markup=create_application_markup(conference_status, position))
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                              text=f'Название работы: {applications[application_index].get("title")}',
                              reply_markup=create_application_markup(conference_status, position))


def get_one_application_info(message): # получить детальную информацию по заявке
    # получение статуса заявки
    conference_status = conferences[users[message.chat.id].conference_index].get('status')

    # TODO: бэкенд
    # applications = fetch_applications(message, conferences[users[message.chat.id].conference_index].get('id'))
    #######################################

    # TODO: эмуляция
    applications = get_applications_from_user(message, users, conferences) # получение списка конференций
    ###############

    # получаем индекс заявки
    application_index = users[message.chat.id].application_index

    # вывод детальной информации по конференции
    display_detailed_application_info(message, applications[application_index], conference_status)


def display_detailed_application_info(message, application, conference_status): # вывод детальной информации по конференции
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                          text=format_application(application),
                          reply_markup=create_detailed_application_markup(conference_status, application.get('email')), # если email = None, то в клавиатуре не будут отрисовываться определенные кнопки
                          parse_mode='HTML')


def submit_new_application(message, edit=False): # инициация процесса подачи новой заявки
    new_application = {'telegram_id': message.chat.id} # создание словаря - тела новой заявки
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    # для редактирования используются те же функции, поэтому нужен флаг edit
    if not edit:
        bot.send_message(message.chat.id,
                         text='<b><u>Внимание! Заявка будет подана только после указания сведений об авторах в окне просмотра заявки!</u></b>\n\n'
                              'Начат процесс подачи заявки.\n'
                              'Если вы передумали подавать заявку, на любом этапе можете нажать на кнопку внизу.\n'
                              'Сначала введите свой номер телефона (10 цифр без "+7". Если вы не хотите указывать номер телефона, напишите "Нет")',
                         reply_markup=create_application_cancellation_markup(),
                         parse_mode='HTML')
    else:
        # TODO: эмуляция
        applications = get_applications_from_user(message, users, conferences)
        ################

        # TODO: бэкенд
        # conference_id = conferences[users[message.chat.id].conference_index].get('id')
        # applications = fetch_applications(message, conference_id)
        ##############

        applications[users[message.chat.id].application_index].pop('phone', None)
        applications[users[message.chat.id].application_index].pop('student_group', None)
        bot.send_message(message.chat.id,
                         text='Запущен процесс редактирования заявки\n'
                              'Сначала введите свой номер телефона (10 цифр без "+7". Если вы не хотите указывать номер телефона, напишите "Нет")')
    bot.register_next_step_handler(message, lambda msg: save_phone_number(msg, new_application, edit))


def save_phone_number(message, new_application, edit=False): # сохранение номера телефона
    reply_markup = None if edit else create_application_cancellation_markup()
    if message.text == 'Отменить заявку': # при нажатии на кнопку
        cancel_application(message)
        return
    regex = r'^\d{10}$' # регулярка
    if message.text.lower() != 'нет' and not re.match(regex, message.text):
        bot.send_message(message.chat.id,
                         'К сожалению, телефон введен в неправильном формате, необходимо повторить ввод',
                         reply_markup=reply_markup)
        bot.register_next_step_handler(message, lambda msg: save_phone_number(msg, new_application, edit))
    else:
        if message.text.lower() != 'нет':
            new_application['phone'] = '+7' + message.text
        bot.send_message(message.chat.id,
                         'Введите название вашего университета (кириллица, цифры и пробел)',
                         reply_markup=reply_markup)
        bot.register_next_step_handler(message, lambda msg: save_university(msg, new_application, edit))


def save_university(message, new_application, edit=False): # сохранение названия университета
    reply_markup = None if edit else create_application_cancellation_markup()
    if message.text == 'Отменить заявку':
        cancel_application(message)
        return
    regex = r'^[А-Яа-я0-9 ]+$'
    if not re.match(regex, message.text):
        bot.send_message(message.chat.id,
                         'К сожалению, название университета введено в неправильном формате, необходимо повторить ввод',
                         reply_markup=reply_markup)
        bot.register_next_step_handler(message, lambda msg: save_university(msg, new_application, edit))
    else:
        new_application['university'] = message.text
        bot.send_message(message.chat.id,
                         'Введите вашу учебную группу\n'
                         'Если вы не хотите указывать учебную группу, напишите "Нет"',
                         reply_markup=reply_markup)
        bot.register_next_step_handler(message, lambda msg: save_student_group(msg, new_application, edit))


def save_student_group(message, new_application, edit=False): # сохранение группы студента
    reply_markup = None if edit else create_application_cancellation_markup()
    if message.text == 'Отменить заявку':
        cancel_application(message)
        return
    if message.text.lower() != 'нет':
        new_application['student_group'] = message.text
    bot.send_message(message.chat.id,
                     'Введите вашу роль на выбор из трех вариантов: "студент", "магистрант", "преподаватель"',
                     reply_markup=reply_markup)
    bot.register_next_step_handler(message, lambda msg: save_applicant_role(msg, new_application, edit))


def save_applicant_role(message, new_application, edit=False): # сохранение роли (студент, магистрант, преподаватель)
    reply_markup = None if edit else create_application_cancellation_markup()
    if message.text == 'Отменить заявку':
        cancel_application(message)
        return
    regex = r'(?i)^(студент|магистрант|преподаватель)$' # игнорирование регистра в регулярке
    if not re.match(regex, message.text):
        bot.send_message(message.chat.id,
                         'К сожалению, роль введена неверно, необходимо повторить ввод',
                         reply_markup=reply_markup)
        bot.register_next_step_handler(message, lambda msg: save_applicant_role(msg, new_application, edit))
    else:
        new_application['applicant_role'] = message.text.lower()
        bot.send_message(message.chat.id,
                         'Введите название вашей учебной работы',
                         reply_markup=reply_markup)
        bot.register_next_step_handler(message, lambda msg: save_title(msg, new_application, edit))


def save_title(message, new_application, edit=False): # сохранение названия заявки
    reply_markup = None if edit else create_application_cancellation_markup()
    if message.text == 'Отменить заявку':
        cancel_application(message)
        return
    new_application['title'] = message.text
    bot.send_message(message.chat.id,
                     'Введите ФИО вашего научного руководителя',
                     reply_markup=reply_markup)
    bot.register_next_step_handler(message, lambda msg: save_adviser(msg, new_application, edit))


def save_adviser(message, new_application, edit=False): # сохранение научного руководителя
    if message.text == 'Отменить заявку':
        cancel_application(message)
        return
    new_application['adviser'] = message.text
    if not edit: # если заявка подается, а не редактируется
        save_new_application(message, new_application) # сохранение заявки в словаре пользователя
        bot.send_message(message.chat.id,'Заявка принята')
    else:  # если происходит редактирование
        applications = get_applications_from_user(message, users, conferences)
        application = applications[users[message.chat.id].application_index] # получение нужной заявки
        application.update(new_application) # обновление данного элемента словаря

        # TODO: бэкенд
        # conference_id = conferences[users[message.chat.id].conference_index].get('id')
        # application_id = application.get('id')
        # patch_application(conference_id, application_id, application)
        ##########################

        bot.send_message(message.chat.id, 'Данные обновлены')
    msg = bot.send_message(message.chat.id, '.') # это сообщение обновится
    get_applications_for_conference(msg) # перейти обратно в меню выбора заявки


def cancel_application(message): # отменить заявку (ReplyKeyboard работает очень костыльно, приходится соответствовать)
    bot.send_message(message.chat.id, 'Заявка не подана', reply_markup=types.ReplyKeyboardRemove())
    message = bot.send_message(message.chat.id, text='.') # это сообщение обновится
    get_applications_for_conference(message)


def submit_authors(message): # добавить основного автора
    applications = get_applications_from_user(message, users, conferences) # получение списка заявок

    applications[users[message.chat.id].application_index].pop('coauthors', None) # если редактирование, то удаление ключа coauthors
    authors_dict = {} # новый словарь для автора и списка соавторов
    bot.send_message(message.chat.id, text='Укажите email автора в формате example@example.example')
    bot.register_next_step_handler(message, lambda msg: save_email(msg, authors_dict, main_author=True)) # для соавторов используются те же функции, для этого нужен флаг main_author


def submit_coauthors(message): # добавить соавтора
    authors_dict = {}
    bot.send_message(message.chat.id, text='Укажите email автора в формате example@example.example')
    bot.register_next_step_handler(message, lambda msg: save_email(msg, authors_dict, main_author=False)) # в данном случае флаг = False


def save_email(message, authors_dict, main_author=False): # сохранение email
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$' # регулярка
    if not re.match(regex, message.text):
        bot.send_message(message.chat.id,
                         'К сожалению, email введен в неправильном формате, необходимо повторить ввод')
        bot.register_next_step_handler(message, lambda msg: save_email(msg, authors_dict, main_author))
    else:
        authors_dict['email'] = message.text
        bot.send_message(message.chat.id,
                         'Введите имя автора (на русском языке с большой буквы)\n')
        bot.register_next_step_handler(message, lambda msg: save_first_name(msg, authors_dict, main_author))


def save_first_name(message, authors_dict, main_author=False): # сохранение имени
    regex = r'^[А-Я][а-я]+$'
    if not re.match(regex, message.text):
        bot.send_message(message.chat.id,
                         'К сожалению, имя введено в неправильном формате, необходимо повторить ввод')
        bot.register_next_step_handler(message, lambda msg: save_first_name(msg, authors_dict, main_author))
    else:
        authors_dict['name'] = message.text
        bot.send_message(message.chat.id,
                         'Введите фамилию автора (на русском языке с большой буквы)')
        bot.register_next_step_handler(message, lambda msg: save_surname(msg, authors_dict, main_author))


def save_surname(message, authors_dict, main_author=False): # сохранение фамилии
    regex = r'^[А-Я][а-я]+$'
    if not re.match(regex, message.text):
        bot.send_message(message.chat.id,
                         'К сожалению, фамилия введена в неправильном формате, необходимо повторить ввод')
        bot.register_next_step_handler(message, lambda msg: save_surname(msg, authors_dict, main_author))
    else:
        authors_dict['surname'] = message.text
        bot.send_message(message.chat.id,
                         'Введите отчество автора (на русском языке с большой буквы)')
        bot.register_next_step_handler(message, lambda msg: save_patronymic(msg, authors_dict, main_author))


def save_patronymic(message, authors_dict, main_author=False): # сохранение отчества
    regex = r'^[А-Я][а-я]+$'
    if not re.match(regex, message.text):
        bot.send_message(message.chat.id,
                         'К сожалению, отчество введено в неправильном формате, необходимо повторить ввод')
        bot.register_next_step_handler(message, lambda msg: save_patronymic(msg, authors_dict))
    else:
        authors_dict['patronymic'] = message.text
        if main_author:
            save_credentials(message, authors_dict) # сохранить данные основного автора
        else: # если происходит добавление соавтора
            applications = get_applications_from_user(message, users, conferences)
            application = applications[users[message.chat.id].application_index] # получение нужной заявки
            application.setdefault('coauthors', []) # при добавлении первого соавтора по ключу coauthors создастся словарь
            application.get('coauthors').append(authors_dict)
            # вывод сообщения и кнопок добавления соавтора
            bot.send_message(message.chat.id,
                             'Соавтор добавлен, для добавления еще одного соавтора нажмите на соответствующую кнопку внизу',
                             reply_markup=create_couathor_markup())


def save_credentials(message, authors_dict): # сохранение информации об основном авторе
    applications = get_applications_from_user(message, users, conferences)
    application = applications[users[message.chat.id].application_index] # получение нужной заявки
    application.update(authors_dict) # сохранение либо обновление полей
    bot.send_message(message.chat.id, 'Основной автор добавлен. Если вы хотите добавить соавтора, нажмите на соответствующую кнопку',
                     reply_markup=create_couathor_markup())


def finalize_application(message): # когда указана информация о соавторах, заявку можно отправлять на сервер

    # TODO: бэкенд
    # applications = fetch_applications(message, conference_id)
    # application = applications[users[message.chat.id].application_index]
    # conference_id = conferences[users[message.chat.id].conference_index].get('id')
    # application_id = application.get('id')
    # if not patch_application(conference_id, application_id, application): # насчет этого не уверен
    #     post_new_application(conference_id, application)

    # отобразить информацию по заявкам
    get_applications_for_conference(message)


def show_article_info(message): # отобразить информацию по статье

    # TODO: бэкенд
    # conference_id = conferences[users[message.chat.id].conference_index].get('id')
    # applications = fetch_applications(message, conference_id)
    # application_id = applications[users[message.chat.id].application_index].get('id')
    # article = fetch_article_by_id(message, conference_id, application_id)
    # if article:
    ############

    # TODO: эмуляция
    application_id = users[message.chat.id].application_index
    if application_id in articles:  # articles - словарь, где ключом является application_id
    ###############

        # TODO: эмуляция
        article = articles.get(application_id) # Если статья уже есть, то вывод информации по ней
        ####################

        review_status = translate_review_status(article.get('review_status')) # перевод review_status на русский
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                              text='К данной заявке уже прикреплена статья.\n'
                                   f'Название статьи: {article.get("publication_title")}\n'
                                   f'Статус рецензирования: {review_status}\n'
                                   f'Дата загрузки: {article.get("upload_date")}\n\n'
                                   f'<b><u>Внимание! При нажатии на кнопку "Прикрепить новую статью" старая статья будет удалена!</u></b>',
                              reply_markup=create_article_markup(),
                              parse_mode='HTML')
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                              text='К данной заявке еще не прикреплена статья',
                              reply_markup=create_article_markup())


def submit_new_article(message): # создание тела новой статьи для отправки на сервер
    new_article = {'telegram_id': message.chat.id}
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                          text='Пожалуйста, введите название статьи')
    bot.register_next_step_handler(message, lambda msg: save_article_title(msg, new_article))


def save_article_title(message, new_article): # сохранение названия статьи
    new_article['publication_title'] = message.text
    bot.send_message(message.chat.id, 'Прикрепите файл статьи в формате doc или docx')
    bot.register_next_step_handler(message, lambda msg: upload_article(msg, new_article))


def upload_article(message, new_article): # загрузка статьи в бота
    if message.document and (message.document.mime_type == 'application/msword' or
                             message.document.mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'): # если прикреплен doc/docx

        # TODO: когда будет готов бэк
        # file_id = message.document.file_id
        # file_info = bot.get_file(file_id)
        # file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        # file_response = requests.get(file_url)
        #
        # if file_response.status_code == 200:
        #     file = {'file': file_response.content}
        #     conference_id = conferences[users[message.chat.id].conference_index].get('id')
        #     applications = fetch_applications(message, conference_id)
        #     application_id = applications[users[message.chat.id].application_index].get('id')
        #     if not fetch_article_by_id(message, conference_id, application_id):
        #         post_article(conference_id, application_id, new_article, file)
        #     else:
        #         patch_article(conference_id, application_id, new_article)
        #         put_article(message, conference_id, application_id, file)
        ###########################

        # TODO: эмуляция
        article_index = users[message.chat.id].application_index
        if article_index not in articles:
            articles[article_index] = {}  # Создаем новый словарь, если ключ отсутствует
        articles[article_index]['publication_title'] = new_article.get('publication_title')
        articles[article_index]['review_status'] = 'in progress'
        articles[article_index]['upload_date'] = datetime.now().date().strftime("%d.%m.%Y")
        ################

        bot.send_message(message.chat.id, 'Статья успешно загружена!')
        message = bot.send_message(message.chat.id, '.') # это сообщение обновится
        show_article_info(message) # отображение информации по статье
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, отправьте файл в формате DOC или DOCX.')
        bot.register_next_step_handler(message, lambda msg: upload_article(msg, new_article))


@bot.callback_query_handler(func=lambda call: True)  # обработка нажатий на кнопки
def callback(call):
    if call.message:
        if call.data == 'display_conferences': # отобразить все конференции
            users[call.message.chat.id].application_index = 0
            get_conferences(call.message)

        elif call.data == 'previous_conference': # перейти к предыдущей конференции
            users[call.message.chat.id].conference_index -= 1
            get_conferences(call.message)

        elif call.data == 'next_conference': # перейти к следующей конференции
            users[call.message.chat.id].conference_index += 1
            get_conferences(call.message)

        elif call.data == 'display_conference_info': # отобразить подробную информацию по конференции
            display_detailed_conference_info(call.message)

        elif call.data == 'display_applications': # посмотреть заявки на конференцию
            get_applications_for_conference(call.message)
            
        elif call.data == 'previous_application': # предыдующая заявка
            users[call.message.chat.id].application_index -= 1
            get_applications_for_conference(call.message)

        elif call.data == 'next_application': # следующая заявка
            users[call.message.chat.id].application_index += 1
            get_applications_for_conference(call.message)
            
        elif call.data == 'display_detailed_application_info': # отобразить полную информацию по заявке и кнопки управления
            get_one_application_info(call.message)

        elif call.data == 'submit_new_application': # загрузить новую заявку
            submit_new_application(call.message)

        elif call.data == 'submit_authors': # добавить информацию об основном авторе
            message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                            text='Заполним информацию об основном авторе.')
            submit_authors(message)

        elif call.data == 'add_coauthor': # добавить соавтора
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                            text='Заполним информацию о соавторе.')
            submit_coauthors(call.message)

        elif call.data == 'finalize_application': # после добавления информации об авторах отправить запрос на бэк
            finalize_application(call.message)

        elif call.data == 'edit_application': # редактировать поля заявки
            submit_new_application(call.message, True)

        elif call.data == 'upload_article': # отобразить информацию по статьям
            show_article_info(call.message)

        elif call.data == 'submit_new_article': # загрузить новую статью
            submit_new_article(call.message)


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)
