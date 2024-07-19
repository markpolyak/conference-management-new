import telebot
import requests
from telebot import types
address="http://localhost"

bot = telebot.TeleBot('7313583878:AAEhpT-01bxTYRFLZLh7gwka5Bpz8H5t3uU')
    
@bot.message_handler(commands=['start']) #Начало работы
def registry(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mero = types.KeyboardButton("Конференции")
    lk = types.KeyboardButton("Поданные заявки")
    markup.add(mero, lk)
    bot.send_message(message.chat.id,'Добро пожаловать, я Misne — твой помощник по регистрации на конференции.', reply_markup=markup)
    
@bot.message_handler(content_types=['text']) # ответ на меню , выбор мероприятий и лк
def mero(message):
    if(message.text == "Конференции"):
        markup_inline =types.InlineKeyboardMarkup()
        past = types.InlineKeyboardButton (text="Прошедшие",callback_data='past')
        open = types.InlineKeyboardButton (text="С открытой регистрацие",callback_data='open')
        future = types.InlineKeyboardButton (text="Будущие",callback_data='future')
        markup_inline.add(past)
        markup_inline.add(open)
        markup_inline.add(future)
        msg=bot.send_message(message.chat.id, 'Какие конференции вы хоитет посмотреть',reply_markup=markup_inline)
    elif(message.text=="Поданные заявки"):
        markup_zayavki=types.InlineKeyboardMarkup()
        zayavki =types.InlineKeyboardButton(text='Поданные заявки',callback_data='zayavki')
        markup_zayavki.add(zayavki)
        response = requests.get(address + "/conferences?filter=past")
        past_confs = set(response.json())
        response = requests.get(address + "/conferences?filter=active")
        active_confs = set(response.json())
        confs = dict(past_confs + active_confs) # прошедшие и текущие конференции
        for conf in confs :
            conf_response = requests.get(address + "/conferences/" + conf.id)
            conf_desc = conf_response.json()
            message_text = "Название: {}\nОрганизатор: {}\nСсылка: {}\nДата начала приема заявок: {}\nДата Окончания приема заявок: {}\nДата начала приема докладов: {}\nДата Окончания приема докладов: {}\nДата начала конференции: {}\nДата Окончания конференции: {}\n".format(
                conf_desc.title, conf_desc.organized_by, conf_desc.url, conf_desc.registrating_start_date, conf_desc.registrating_end_date, conf_desc.submission_start_date, conf_desc.submission_end_date, conf_desc.conf_start_date, conf_desc.conf_end_date
            )
            bot.send_message(message.chat.id, message_text,reply_markup=markup_zayavki)
        
def handle_docs(message,conf_id,zayavka_id):
        if message.document is None:
            msg=bot.send_message(text="Отправьте ljrevtyn!")
            bot.register_next_step_handler(msg,handle_docs,conf_id,zayavka_id)
        else:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            response = requests.post(address + "/conferences/" + conf_id + "/applications/" + zayavka_id + "/publication", files={message.document.name, downloaded_file})
            bot.reply_to(message, "Файл сохранен")

        
def reg_name(message,info):
    name = message.text
    info['name']=name
    msg=bot.send_message(message.chat.id,'Ведите Фамилия')
    bot.register_next_step_handler(msg,reg_surname,info)
    
def reg_surname(message,info):
    surname = message.text
    info['surname']=surname
    msg=bot.send_message(message.chat.id,'Ведите Очество ')
    bot.register_next_step_handler(msg,reg_patronumic,info)
    
def reg_patronumic(message,info):
    patronumic = message.text
    info['patronumic']=patronumic
    msg=bot.send_message(message.chat.id,'Ведите университет')
    bot.register_next_step_handler(msg,reg_university,info)
    
def reg_university(message,info):
    university=message.text
    info['university']=university
    markuprole =types.ReplyKeyboardMarkup(resize_keyboard=True)
    student = types.KeyboardButton (text="Студент") 
    teacher = types.KeyboardButton (text="Преподаватель")
    markuprole.add(student,teacher)
    msg=bot.send_message(message.chat.id,'Выберите статус (студент/преподаватель)',reply_markup=markuprole)
    bot.register_next_step_handler(msg,reg_applicant_role,info)
    
def reg_applicant_role(message,info):
    applicant_role=message.text
    info['applicant_role']=applicant_role
    if applicant_role.lower() =='студент':
        msg=bot.send_message(message.chat.id,'Введите группу') 
        bot.register_next_step_handler(msg,reg_student_group,info)
    else : 
        info['student_group']=''
        msg=bot.send_message(message.chat.id,'Введите email')
        bot.register_next_step_handler(msg,reg_email,info)
    
def reg_student_group(message,info):
    student_group=message.text
    info['student_group']=student_group
    msg=bot.send_message(message.chat.id,'Введите email') 
    bot.register_next_step_handler(msg,reg_email,info)   

def reg_email(message, info):
    email = message.text
    info['email']=email
    msg=bot.send_message(message.chat.id, "Введите телефон")     
    bot.register_next_step_handler(msg,reg_phone,info)  

def reg_phone(message, info):
    phone = message.text
    info['phone']=phone
    msg=bot.send_message(message.chat.id, "Введите название работы")
    bot.register_next_step_handler(msg,reg_title,info)

def reg_title(message, info):
    title = message.text
    info['title']=title
    msg=bot.send_message(message.chat.id, "Введите Руководителя")
    bot.register_next_step_handler(msg,reg_adviser,info)
    
def reg_adviser(message, info):
    adviser = message.text
    info['adviser']=adviser
    markuprole_inline =types.ReplyKeyboardMarkup(resize_keyboard=True)
    adviser_yes = types.KeyboardButton (text="Добавить соавтора") 
    adviser_no = types.KeyboardButton (text="Не добавлять соавтора")
    markuprole_inline.add(adviser_yes)
    markuprole_inline.add(adviser_no)
    info['coauthors'] = {}
    msg=bot.send_message(message.chat.id, "Есть ли у вас соавторы?",reply_markup=markuprole_inline)
    bot.register_next_step_handler(msg,reg_soavtor,info)
    
def reg_soavtor(message,info):
    if message.text.lower()=="добавить соавтора":
        soavtor_inf={}
        msg=bot.send_message(message.chat.id,text="Введите Имя соавтора")
        bot.register_next_step_handler(msg,reg_soavtor_name, info, soavtor_inf)
    else : 
        conf_id = info['conf_id']
        response = requests.post(address + "/conferences/" + conf_id + "/applications", json=info.__dict__)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        mero = types.KeyboardButton("Конференции")
        lk = types.KeyboardButton("Поданные заявки")
        markup.add(mero, lk)
        msg=bot.send_message(message.chat.id, "Сохранено",reply_markup=markup)
        
        
        
def reg_soavtor_name(message,info, soavtor_inf):
    soa_name=message.text
    soavtor_inf['name']=soa_name
    msg=bot.send_message(message.chat.id,text="Введите Фамилию соавтора")
    bot.register_next_step_handler(msg,reg_soavtor_surname,info, soavtor_inf)
        
def reg_soavtor_surname(message,info, soavtor_inf):
    soa_surname=message.text
    soavtor_inf['surname']=soa_surname
    msg=bot.send_message(message.chat.id,text="Введите Очество соавтора")
    bot.register_next_step_handler(msg,reg_soavtor_patronymic,info, soavtor_inf)
    
def reg_soavtor_patronymic(message, info, soavtor_inf):
    soa_patronymic=message.text
    soavtor_inf['patronymic']=soa_patronymic
    msg=bot.send_message(message.chat.id,text="Введите email соавтора")
    bot.register_next_step_handler(msg,reg_soavtor_email,info, soavtor_inf)
    
def reg_soavtor_email(message,soavtor_inf, info):
    soa_email=message.text
    soavtor_inf['email']=soa_email
    info['coauthors'].add(soavtor_inf)
    msg=bot.send_message(message.chat.id,text="Добавленно")
    markuprole_inline =types.ReplyKeyboardMarkup(resize_keyboard=True)
    adviser_yes = types.KeyboardButton (text="Добавить соавтора") 
    adviser_no = types.KeyboardButton (text="Не добавлять соавтора")
    markuprole_inline.add(adviser_yes)
    markuprole_inline.add(adviser_no)
    msg=bot.send_message(message.chat.id, "Добавить еще соавторов?",reply_markup=markuprole_inline)
    bot.register_next_step_handler(msg,reg_soavtor, info)
    
@bot.callback_query_handler(func= lambda call: True)
def answer(call):
    if call.data =='past':
        response = requests.get(address + "/conferences?filter=past")
        conference_list = response.json()
        for conf in conference_list:
            msg=bot.send_message(call.message.chat.id, conf.name_rus_short+"/n"+conf.name_eng_short+"/n"+"Дата начала проведения конференции "+ conf.conf_start_date+"/n"+"Дата завершения конференции "+conf.conf_end_date) 
    elif call.data=='open':
        response = requests.get(address + "/conferences?filter=active")
        conference_list = response.json()
        for conf in conference_list:
            btn_reg=types.InlineKeyboardMarkup()
            reg = types.InlineKeyboardButton (text="Зарегистрироваться",callback_data='reg_mero|'+conf.id)
            btn_reg.add(reg)
            msg=bot.send_message(call.message.chat.id, conf.name_rus_short+"/n"+conf.name_eng_short+"/n"+"Дата начала проведения конференции "+ conf.conf_start_date+"/n"+"Дата завершения конференции "+conf.conf_end_date,reply_markup=btn_reg)
    elif call.data =='future':
        response = requests.get(address + "/conferences?filter=future")
        conference_list = response.json()
        for conf in conference_list:
            msg=bot.send_message(call.message.chat.id, conf.name_rus_short+"/n"+conf.name_eng_short+"/n"+"Дата начала проведения конференции "+ conf.conf_start_date+"/n"+"Дата завершения конференции "+conf.conf_end_date)
    elif 'reg_mero' in call.data :
        conf_id=int(call.data.split("|")[1])
        bot.send_message(call.message.chat.id,'Давай заполним необходимую информацию.')
        msg=bot.send_message(call.message.chat.id,'Пожалуйста, укажи Имя.')
        info={}
        info['telegram_id']=call.from_user.id
        info['conf_id']=conf_id
        bot.register_next_step_handler(msg,reg_name,info)   
    elif 'update' in call.data :  
        conf_id=int(call.data.split("|")[1])
        zayavka_id=int(call.data.split("|")[2])
        msg=bot.send_message(call.message.chat.id,'Введите данные заново.Пожалуйста, укажи своё имя.')
        info={}
        info['telegram_id']=call.from_user.id
        bot.register_next_step_handler(msg,reg_name,info)
    elif 'zayavki' in call.data:
        conf_id=int(call.data.split("|")[1])
        response = requests.get(address + "/conferences/" + conf_id + "/applications?telegram_id=" + call.from_user.id)
        zayavki = response.json()
        for zayavka in zayavki: 
            btn_article_inline = types.InlineKeyboardMarkup()
            update = types.InlineKeyboardButton(text='Изменить данные',callback_data='update|'+conf.id+'|'+zayavka.id) 
            add_article = types.InlineKeyboardButton(text='Добавить статью', callback_data='add_article|'+conf.id+'|'+zayavka.id)
            btn_article_inline.add(update)
            btn_article_inline.add(add_article)
            submit_date = zayavka.submitted_at
            update_date = zayavka.updated_at
            title = zayavka.title
            adviser = zayavka.adviser
            soavtori = zayavka.coauthors
            message = "Работа: {}\nРуководитель: {}\nДата подачи: {}\nДата последнего изменения: {}\nСоавторы: ".format(title, adviser, submit_date, update_date)
            if len(soavtori) == 0:
                message = message + "Нет"
            else:
                for soavtor in soavtori:
                    message = message + "\n" + soavtor
            bot.send_message(call.message.chat.id, message, reply_markup=btn_article_inline) #инфо о заявке
    elif 'add_article' in call.data :
        conf_id=int(call.data.split("|")[1])
        zayavka_id=int(call.data.split("|")[2])
        msg=bot.send_message(call.message.chat.id, 'Отправте документ')
        bot.register_next_step_handler(msg,handle_docs,conf_id,zayavka_id)
         
bot.polling(none_stop=True) 