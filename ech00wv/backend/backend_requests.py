import requests
from config.config import base_http


def fetch_all_conferences(conference_filter): # GET /conferences?filter=...
    url = f'{base_http}/conferences'
    params = {'filter': conference_filter}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        fetched_conferences = response.json()
        return fetched_conferences
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return []


def fetch_conference_by_id(conference_id): # GET /conferences{conference_id}
    url = f'{base_http}/conferences/{conference_id}'
    response = requests.get(url)
    if response.status_code == 200:
        fetched_conference = response.json()
        return fetched_conference
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return None


# функция, которая получает те конференции, срок подачи заявок по которым уже прошел, однако у пользователя поданы заявки
def fetch_past_conferences_with_applications(message): # GET /conferences/{conference.get("id")}/applications?telegram_id=...
    filtered_conferences = []
    past_conferences = fetch_all_conferences('past')
    params = {'telegram_id': message.chat.id}
    for conference in past_conferences:
        url = f'{base_http}/conferences/{conference.get("id")}/applications'
        response = requests.get(url, params=params)
        if response.status_code == 200:
            filtered_conferences.append(conference)
    return filtered_conferences


def fetch_applications(message, conference_id): # GET /conferences/{conference_id}/applications?telegram_id=...
    url = f'{base_http}/conferences/{conference_id}/applications'
    params = {'telegram_id': message.chat.id}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        applications = response.json()
        return applications
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return None


def post_new_application(conference_id, application): # POST /conferences/{conference_id}/applications
    url = f'{base_http}/conferences/{conference_id}/applications'
    response = requests.post(url, json=application)
    if response.status_code == 200:
        print("Заявка успешно отправлена!")
        return True
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        print(response.text)
        return False



# редактирование заявки
def patch_application(conference_id, application_id, application): # PATCH /conferences/{conference_id}/applications/{application_id}
    url =f'{base_http}/conferences/{conference_id}/applications/{application_id}'
    response = requests.patch(url, json=application)
    if response.status_code == 200:
        print("Запрос выполнен успешно")
        return response.json()
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return None


def fetch_article_by_id(message, conference_id, application_id): # GET /{conference_id}/applications/{application_id}/publication?telegram_id=...
    url = f'{base_http}/conferences/{conference_id}/applications/{application_id}/publication'
    params = {'telegram_id': message.chat.id}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("Запрос выполнен успешно")
        return response.json()
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return None


# Отправить файл статьи
def post_article(conference_id, application_id, body, file): # POST /{conference_id}/applications/{application_id}/publication
    url = f'{base_http}/conferences/{conference_id}/applications/{application_id}/publication'
    response = requests.post(url, json=body, files=file)
    if response.status_code == 200:
        print("Статья успешно загружена")
        return True
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return False


# Редактировать файл статьи
def put_article(message, conference_id, application_id, file): # PUT /{conference_id}/applications/{application_id}/publication?telegram_id=...
    url = f'{base_http}/conferences/{conference_id}/applications/{application_id}/publication'
    params = {'telegram_id': message.chat.id}
    response = requests.put(url, files=file, params=params)
    if response.status_code == 200:
        print("Статья успешно обновлена")
        return True
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return False


def patch_article(conference_id, application_id, body): # PATCH /conferences/{conference_id}/applications/{application_id}/publication
    url = f'{base_http}/conferences/{conference_id}/applications/{application_id}/publication'
    response = requests.patch(url, json=body)
    if response.status_code == 200:
        print("Данные успешно обновлены")
        return True
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return False
        
print(base_http)
