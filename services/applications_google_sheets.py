import gspread
import json
from datetime import datetime
from typing import Optional
import smtplib
from functools import reduce

from helpers.conference_helper import get_conferences, get_conference_sheet_id, get_sheet_by_id, get_authors_by_id
from services.mail_mailru import send_mail


def get_applications(conference_id, email: Optional[str] = None, telegram_id: Optional[str] = None, discord_id: Optional[str] = None):
    sheet_id = get_conference_sheet_id(conference_id)
    if not sheet_id:
        raise Exception("Конференция с таким id не найдена")

    sheet = get_sheet_by_id(sheet_id)
    records = sheet.get_all_records()

    filtered_records = []

    for record in records:
        if (email and record['email'] == email) or (telegram_id and record['telegram_id'] == telegram_id) or (discord_id and record['discord_id'] == discord_id):
            record['coauthors'] = []

            authors_sheet = get_authors_by_id(sheet_id)
            authors_records = authors_sheet.get_all_records()

            for author_record in authors_records:
                if author_record['id'] == record['id'] and author_record['email'] != record['email']:
                    record['coauthors'].append({'name': author_record['name'], 'surname': author_record['surname'], 'patronymic': author_record['patronymic']})

            filtered_records.append(record)
    return filtered_records


def add_application(conference_id, application):
    sheet_id = get_conference_sheet_id(conference_id)
    if not sheet_id:
        raise Exception("Конференция с таким id не найдена")

    sheet = get_sheet_by_id(sheet_id)

    record = application.dict()

    id = reduce(lambda x, y: x if x['id'] > y['id'] else y, sheet.get_all_records())['id'] + 1

    record['id'] = id
    record['submitted_at'] = datetime.now().astimezone().isoformat()
    record['updated_at'] = record['submitted_at']

    authors_sheet = get_authors_by_id(sheet_id)

    # Добавление самого автора
    authors_sheet.append_row([record['id'], record['email'], record['name'], record['surname'], record['patronymic']])

    # Добавление соавторов
    for coauthor in record['coauthors']:
        authors_sheet.append_row(
            [record['id'], coauthor['email'], coauthor['name'], coauthor['surname'], coauthor['patronymic']])

    temp_coauthors = record['coauthors']
    record['coauthors'] = None

    sheet.append_row(list(record.values()))

    record['coauthors'] = temp_coauthors

    return record


def update_application(conference_id, application_id, application):
    sheet_id = get_conference_sheet_id(conference_id)
    if not sheet_id:
        raise Exception("Конференция с таким id не найдена")

    sheet = get_sheet_by_id(sheet_id)
    records = sheet.get_all_records()
    for i, record in enumerate(records):
        if record['id'] == application_id:
            if (
                    (application.telegram_id is None or application.telegram_id != str(record['telegram_id']))
                    and
                    (application.discord_id is None or application.discord_id != str(record['discord_id']))
            ):
                return None
            for key, value in application.dict().items():
                if value is not None and key != 'telegram_id' and key != 'discord_id' and key != 'id' and key != 'submitted_at':
                    record[key] = value

            record['updated_at'] = datetime.now().astimezone().isoformat()

            sheet.update(f'A{i + 2}', [list(record.values())])

            record['coauthors'] = []

            authors_sheet = get_authors_by_id(sheet_id)
            authors_records = authors_sheet.get_all_records()

            for author_record in authors_records:
                if author_record['id'] == record['id'] and author_record['email'] != record['email']:
                    record['coauthors'].append({'name': author_record['name'], 'surname': author_record['surname'],
                                                'patronymic': author_record['patronymic']})

            return record
    return None


def delete_application(conference_id, application_id, email: Optional[str] = None, telegram_id: Optional[str] = None, discord_id: Optional[str] = None):
    sheet_id = get_conference_sheet_id(conference_id)
    if not sheet_id:
        raise Exception("Конференция с таким id не найдена")

    sheet = get_sheet_by_id(sheet_id)
    records = sheet.get_all_records()

    for i, record in enumerate(records):
        if record['id'] == application_id:
            if (
                    (email and record['email'] == email)
                    or
                    (telegram_id and record['telegram_id'] == telegram_id)
                    or
                    (discord_id and record['discord_id'] == discord_id)
            ):
                try:
                    send_mail(to=record['email'], conference_id=conference_id, author_id=record['id'])
                except smtplib.SMTPException as err:
                    raise err

                return {"message": "Для отмены заявки на участие в конференции свяжитесь с организаторами"}

    return None
