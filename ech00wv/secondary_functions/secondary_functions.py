from datetime import datetime


def format_application(application): # форматирование текста заявки
    coauthors = "\n".join(
        f"  Имя: {coauthor['name']}\n"
        f"  Фамилия: {coauthor['surname']}\n"
        f"  Отчество: {coauthor['patronymic']}\n"
        f"  Email: {coauthor['email']}\n"
        for coauthor in application.get('coauthors', [])
    )

    formatted_output = (
        f"Email автора: {application.get('email', 'Еще не указан')}\n"
        f"Телефон: {application.get('phone', 'Отсутствует')}\n"
        f"Имя автора: {application.get('name', 'Еще не указано')}\n"
        f"Фамилия автора: {application.get('surname', 'Еще не указана')}\n"
        f"Отчество автора: {application.get('patronymic', 'Еще не указано')}\n"
        f"Университет: {application.get('university')}\n"
        f"Учебная группа: {application.get('student_group', 'Отсутствует')}\n"
        f"Роль заявителя: {application.get('applicant_role')}\n"
        f"Название работы: {application.get('title')}\n"
        f"Научный руководитель: {application.get('adviser')}\n"
        f"Соавторы:\n{coauthors if coauthors else 'Отсутствуют'}\n\n"
        f"{'<b><u>Редактирование заявки и загрузка статьи будут доступны только после указания сведений об авторах!</u></b>' if application.get('email') is None else ''}"
    )

    return formatted_output


def get_submission_status(start_date, end_date): # получить статус для каждого из событий
    today = datetime.now().date()
    start_date = datetime.strptime(start_date, "%d.%m.%Y").date()
    end_date = datetime.strptime(end_date, "%d.%m.%Y").date()

    if today < start_date:
        return "still_closed"
    elif start_date <= today <= end_date:
        return "is_opened"
    else:
        return "already_closed"


def add_status_to_conference(conference): # добавить статус к каждой из заявок
    from backend.backend_requests import fetch_conference_by_id
    # todo: когда будет готов бэк
    # detailed_conference = fetch_conference_by_id(conference.get('id'))
    detailed_conference = fetch_conference_by_id_test(conference.get('id'))
    conference['status'] = {
        "application_status": get_submission_status(detailed_conference.get('registration_start_date'), detailed_conference.get('registration_end_date')),
        "article_status": get_submission_status(detailed_conference.get('submission_start_date'), detailed_conference.get('submission_end_date')),
        "conference_status": get_submission_status(detailed_conference.get('conf_start_date'), detailed_conference.get('conf_end_date'))
    }
    return conference


def get_applications_from_user(message, users, conferences): # получить список заявок по конференции
    conference_index = users[message.chat.id].conference_index
    # получаем саму конференцию
    conference = conferences[conference_index]
    return users[message.chat.id].applications.get(conference.get('id'))


def fetch_all_conferences_test(conference_filter): # получить краткий список конференций
    if conference_filter == 'past':
        return [
            {
                "id": 1,
                "name_rus_short": "Завершенная конференция 1",
                "name_eng_short": "Completed Conference 1",
                "conf_start_date": "10.01.2023",
                "conf_end_date": "15.01.2023"
            }
        ]
    else:
        return [
            {
                "id": 2,
                "name_rus_short": "Будущая конференция 2",
                "name_eng_short": "Upcoming Conference 2",
                "conf_start_date": "23.07.2024",
                "conf_end_date": "29.07.2024"
            },
            {
                "id": 3,
                "name_rus_short": "Будущая конференция 3",
                "name_eng_short": "Upcoming Conference 3",
                "conf_start_date": "20.08.2024",
                "conf_end_date": "25.08.2024"
            }
        ]


#todo: ТЕСТОВОЕ ПОЛУЧЕНИЕ КОНФЕРЕНЦИИ
def fetch_conference_by_id_test(conference_id): # получить полную информацию по конференции
    detailed_conferences = [
        {
            "id": 1,
            "name_rus": "Завершенная конференция 1 на русском языке",
            "name_rus_short": "Завершенная конференция 1",
            "name_eng": "Completed Conference 1 in English",
            "name_eng_short": "Completed Conference 1",
            "registration_start_date": "01.12.2022",
            "registration_end_date": "05.01.2023",
            "submission_start_date": "06.01.2023",
            "submission_end_date": "09.01.2023",
            "conf_start_date": "10.01.2023",
            "conf_end_date": "15.01.2023",
            "organized_by": "Организация примера 1",
            "url": "https://example.com/conference",
            "email": "contact1@example.com"
        },
        {
            "id": 2,
            "name_rus": "Будущая конференция 2 на русском языке",
            "name_rus_short": "Будущая конференция 2",
            "name_eng": "Upcoming Conference 2 in English",
            "name_eng_short": "Upcoming Conference 2",
            "registration_start_date": "01.05.2024",
            "registration_end_date": "20.07.2024",
            "submission_start_date": "16.06.2024",
            "submission_end_date": "20.07.2024",
            "conf_start_date": "23.07.2024",
            "conf_end_date": "29.07.2024",
            "organized_by": "Организация примера 2",
            "url": "https://example.com/upcoming-conference-2",
            "email": "contact2@example.com"
        },
        {
            "id": 3,
            "name_rus": "Будущая конференция 3 на русском языке",
            "name_rus_short": "Будущая конференция 3",
            "name_eng": "Upcoming Conference 3 in English",
            "name_eng_short": "Upcoming Conference 3",
            "registration_start_date": "01.07.2024",
            "registration_end_date": "15.08.2024",
            "submission_start_date": "16.08.2024",
            "submission_end_date": "19.08.2024",
            "conf_start_date": "20.08.2024",
            "conf_end_date": "25.08.2024",
            "organized_by": "Организация примера 3",
            "url": "https://example.com/upcoming-conference-3",
            "email": "contact3@example.com"
        }
    ]
    for conference in detailed_conferences:
        if conference.get('id') == conference_id:
            return conference
    return None


def translate_review_status(review_status): # перевести статус обработки заявки
    if review_status == "in progress":
        return "в процессе обработки"
    elif review_status == "changes requested":
        return "запрошены изменения"
    elif review_status == "rejected":
        return "отклонено"
    elif review_status == "accepted":
        return "принято"
