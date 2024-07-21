from telebot import types


def create_conferences_markup(position):  # создание кнопок для отображения информации по конференциям
    markup = types.InlineKeyboardMarkup(row_width=1)
    if position == 'first':
        markup.add(types.InlineKeyboardButton('>', callback_data='next_conference'))
    elif position == 'last':
        markup.add(types.InlineKeyboardButton('<', callback_data='previous_conference'))
    elif position == 'mid':
        markup.add(types.InlineKeyboardButton('<', callback_data='previous_conference'),
                   types.InlineKeyboardButton('>', callback_data='next_conference'))
    markup.add(types.InlineKeyboardButton('Просмотреть список заявок либо подать новую заявку', callback_data='display_applications'),
               types.InlineKeyboardButton('Просмотреть подробную информацию о конференции', callback_data='display_conference_info'))
    return markup


def create_detailed_conference_markup():  # создание кнопок для отображения подробной информации по конференции
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton('Назад к списку конференций', callback_data='display_conferences'))
    return markup


def create_application_markup(conference_status, position): # создание кнопок для отображения информации по заявкам
    markup = types.InlineKeyboardMarkup(row_width=1)
    if position == 'first':
        markup.add(types.InlineKeyboardButton('>', callback_data='next_application'))
    elif position == 'last':
        markup.add(types.InlineKeyboardButton('<', callback_data='previous_application'))
    elif position == 'mid':
        markup.add(types.InlineKeyboardButton('<', callback_data='previous_application'),
                   types.InlineKeyboardButton('>', callback_data='next_application'))
    if position != 'none':
        markup.add(types.InlineKeyboardButton('Просмотреть заявку', callback_data='display_detailed_application_info'))
    if conference_status.get('application_status') == 'is_opened':
        markup.add(types.InlineKeyboardButton('Подать новую заявку', callback_data='submit_new_application'))
    markup.add(types.InlineKeyboardButton('Назад', callback_data='display_conferences'))
    return markup


def create_couathor_markup(): # создание кнопок для добавления очередного соавтора
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('Добавить еще одного соавтора', callback_data='add_coauthor'),
               types.InlineKeyboardButton('Соавторов больше нет', callback_data='finalize_application'))
    return markup


def create_application_cancellation_markup(): # создание кнопки для отмены подачи заявки
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Отменить заявку')
    return markup


def create_detailed_application_markup(conference_status, is_completed): # создание кнопок для управления заявкой
    markup = types.InlineKeyboardMarkup(row_width=1)

    if conference_status.get('application_status') == 'is_opened':
        markup.add(types.InlineKeyboardButton('Указать либо редактировать сведения об авторах', callback_data='submit_authors'))
        if is_completed:
            markup.add(types.InlineKeyboardButton('Редактировать заявку', callback_data='edit_application'))
            if conference_status.get('article_status') == 'is_opened':
                markup.add(types.InlineKeyboardButton('Загрузить статью', callback_data='upload_article'))

    markup.add(types.InlineKeyboardButton('Назад', callback_data='display_applications'))
    return markup


def create_article_markup(): # создание кнопок для управления статьями
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('Прикрепить новую статью', callback_data='submit_new_article'),
        types.InlineKeyboardButton('Назад', callback_data='display_detailed_application_info'))
    return markup
