from googleapiclient.discovery import build
from .config import credentials, SPREADSHEET_ID
from fastapi import HTTPException
from .models import Conference
from datetime import datetime
from typing import List
from .models import Application, Coauthor
from .schemas import ApplicationResponse, ConferenceResponse
from .config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_EMAIL

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_service():
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    return sheet

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").isoformat()
    except ValueError:
        return None


def get_conferences(filter: str = 'active') -> List[Conference]:
    sheet = get_service()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='A2:O').execute()
    values = result.get('values', [])
    conferences = []
    current_time = datetime.now().isoformat()

    for row in values:
        conf = Conference(
            id=row[0],
            sheet_id=row[1],
            full_name=row[2],
            short_name=row[3],
            full_name_eng=row[4] if len(row) > 4 else None,
            short_name_eng=row[5] if len(row) > 5 else None,
            organization=row[6],
            application_start=parse_date(row[7]),
            application_end=parse_date(row[8]),
            report_start=parse_date(row[9]),
            report_end=parse_date(row[10]),
            conference_start=parse_date(row[11]),
            conference_end=parse_date(row[12]),
            website=row[13] if len(row) > 13 else None,
            contact_email=row[14]
        )

        if filter == 'all':
            conferences.append(conf)
        elif filter == 'active':
            if conf.application_start <= current_time <= conf.application_end:
                conferences.append(conf)
        elif filter == 'past':
            if conf.application_end < current_time:
                conferences.append(conf)
        elif filter == 'future':
            if conf.application_start > current_time:
                conferences.append(conf)

    return conferences

def get_conference_responses(filter: str = 'active') -> List[ConferenceResponse]:
    conferences = get_conferences(filter)
    response = []
    for conf in conferences:
        conference_info = ConferenceResponse(
            id=conf.id,
            name_rus_short=conf.short_name,
            name_eng_short=conf.short_name_eng,
            conf_start_date=conf.conference_start,
            conf_end_date=conf.conference_end
        )
        response.append(conference_info)
    return response

def get_conference_by_id(conference_id: int) -> Conference | None:
    sheet = get_service()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='A2:O').execute()
    values = result.get('values', [])

    for row in values:
        if int(row[0]) == conference_id:
            return Conference(
                id=row[0],
                sheet_id=row[1],
                full_name=row[2],
                short_name=row[3],
                full_name_eng=row[4] if len(row) > 4 else None,
                short_name_eng=row[5] if len(row) > 5 else None,
                organization=row[6],
                application_start=parse_date(row[7]),
                application_end=parse_date(row[8]),
                report_start=parse_date(row[9]),
                report_end=parse_date(row[10]),
                conference_start=parse_date(row[11]),
                conference_end=parse_date(row[12]),
                website=row[13] if len(row) > 13 else None,
                contact_email=row[14]
            )
    return None
def add_application(conference_id: int, application: Application) -> ApplicationResponse:
    sheet = get_service()
    current_time = datetime.now().isoformat()

    coauthors_list = []
    for coauthor in (application.coauthors or []):
        coauthors_list.append(f"{coauthor.surname} {coauthor.name} {coauthor.patronymic}")
    coauthors_str = ", ".join(coauthors_list)

    new_row = [
        application.telegram_id,
        application.discord_id,
        current_time,
        current_time,
        application.email,
        application.phone,
        application.name,
        application.surname,
        application.patronymic,
        application.university,
        application.student_group,
        application.applicant_role,
        application.title,
        application.adviser,
        coauthors_str
    ]

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='A2:O').execute()
    values = result.get('values', [])
    sheet_id = None
    for row in values:
        if int(row[0]) == conference_id:
            sheet_id = row[1]
            break

    if not sheet_id:
        raise ValueError("Conference not found")

    result = sheet.values().append(
        spreadsheetId=sheet_id,
        range='A2',
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body={'values': [new_row]}
    ).execute()

    updated_range = result['updates']['updatedRange']
    start_row = int(updated_range.split('!')[1].split(':')[0][1:])

    return ApplicationResponse(
        id=start_row,
        telegram_id=application.telegram_id,
        discord_id=application.discord_id,
        submitted_at=current_time,
        updated_at=current_time,
        email=application.email,
        phone=application.phone,
        name=application.name,
        surname=application.surname,
        patronymic=application.patronymic,
        university=application.university,
        student_group=application.student_group,
        applicant_role=application.applicant_role,
        title=application.title,
        adviser=application.adviser,
        coauthors=application.coauthors or [],
        conference_id=conference_id
    )

def update_application(conference_id: int, application_id: int, update_data: dict) -> ApplicationResponse:
    sheet = get_service()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='A2:O').execute()
    values = result.get('values', [])
    sheet_id = None
    for row in values:
        if int(row[0]) == conference_id:
            sheet_id = row[1]
            break

    if not sheet_id:
        raise ValueError("Conference not found")

    application_row = application_id

    result = sheet.values().get(spreadsheetId=sheet_id, range=f'A{application_row}:O{application_row}').execute()
    values = result.get('values', [])

    if not values:
        raise ValueError("Application not found")

    application_data = values[0]

    if 'telegram_id' in update_data:
        if update_data['telegram_id'] != application_data[0]:
            raise HTTPException(status_code=403, detail="Invalid telegram_id")
    elif 'discord_id' in update_data:
        if update_data['discord_id'] != application_data[1]:
            raise HTTPException(status_code=403, detail="Invalid discord_id")
    else:
        raise HTTPException(status_code=403, detail="No telegram_id or discord_id provided for verification")

    current_time = datetime.now().isoformat()
    update_data['updated_at'] = current_time

    if 'coauthors' in update_data and not update_data['coauthors']:
        coauthors_str = application_data[14]
    else:
        coauthors = update_data.get('coauthors', [])
        coauthors_str = ", ".join([f"{coauthor['name']} {coauthor['surname']} {coauthor['patronymic']}" for coauthor in coauthors])

    updated_row = [
        application_data[0],  # telegram_id
        update_data.get('discord_id', application_data[1]),  # discord_id
        application_data[2],  # submitted_at
        update_data.get('updated_at', application_data[3]),
        update_data.get('email', application_data[4]),
        update_data.get('phone', application_data[5]),
        update_data.get('name', application_data[6]),
        update_data.get('surname', application_data[7]),
        update_data.get('patronymic', application_data[8]),
        update_data.get('university', application_data[9]),
        update_data.get('student_group', application_data[10]),
        update_data.get('applicant_role', application_data[11]),
        update_data.get('title', application_data[12]),
        update_data.get('adviser', application_data[13]),
        coauthors_str
    ]

    sheet.values().update(
        spreadsheetId=sheet_id,
        range=f'A{application_row}:O{application_row}',
        valueInputOption='USER_ENTERED',
        body={'values': [updated_row]}
    ).execute()

    coauthors_list = []
    if coauthors_str:
        for coauthor in coauthors_str.split(','):
            parts = coauthor.strip().split()
            if len(parts) == 3:
                coauthors_list.append(Coauthor(
                    surname=parts[0],
                    name=parts[1],
                    patronymic=parts[2]
                ))

    return ApplicationResponse(
        id=application_id,
        telegram_id=updated_row[0],
        discord_id=updated_row[1],
        submitted_at=updated_row[2],
        updated_at=updated_row[3],
        email=updated_row[4],
        phone=updated_row[5],
        name=updated_row[6],
        surname=updated_row[7],
        patronymic=updated_row[8],
        university=updated_row[9],
        student_group=updated_row[10],
        applicant_role=updated_row[11],
        title=updated_row[12],
        adviser=updated_row[13],
        coauthors=coauthors_list,
        conference_id=conference_id
    )

def delete_application(conference_id: int, application_id: int, delete_data: dict):
    sheet = get_service()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='A2:O').execute()
    values = result.get('values', [])
    sheet_id = None
    for row in values:
        if int(row[0]) == conference_id:
            sheet_id = row[1]
            break

    if not sheet_id:
        raise ValueError("Conference not found")

    application_row = application_id
    result = sheet.values().get(spreadsheetId=sheet_id, range=f'A{application_row}:O{application_row}').execute()
    values = result.get('values', [])

    if not values:
        raise ValueError("Application not found")

    application_data = values[0]

    if 'telegram_id' in delete_data:
        if delete_data['telegram_id'] != application_data[0]:
            raise HTTPException(status_code=403, detail="Invalid telegram_id")
    elif 'discord_id' in delete_data:
        if delete_data['discord_id'] != application_data[1]:
            raise HTTPException(status_code=403, detail="Invalid discord_id")
    elif 'email' in delete_data:
        if delete_data['email'] != application_data[4]:
            raise HTTPException(status_code=403, detail="Invalid email")
    else:
        raise HTTPException(status_code=403, detail="No valid identifier provided for verification")

    organizer_email = get_conference_organizer_email(conference_id)
    send_email_notification(organizer_email, delete_data, application_id)

    return {"message": "Для отмены заявки на участие в конференции свяжитесь с организаторами"}

def get_conference_organizer_email(conference_id: int) -> str:
    sheet = get_service()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='A2:O').execute()
    values = result.get('values', [])

    for row in values:
        if int(row[0]) == conference_id:
            return row[14]

    raise ValueError("Conference not found")

def send_email_notification(organizer_email: str, delete_data: dict, application_id: int):
    subject = "Request to Delete Application"
    body = f"User {delete_data} has requested to delete application ID: {application_id} at {datetime.now().isoformat()}"

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = organizer_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, organizer_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def get_user_applications(telegram_id: str) -> List[ApplicationResponse]:
    sheet = get_service()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='A2:O').execute()
    values = result.get('values', [])
    applications = []

    for row in values:
        sheet_id = row[1]
        app_result = sheet.values().get(spreadsheetId=sheet_id, range='A2:O').execute()
        app_values = app_result.get('values', [])
        for index, app_row in enumerate(app_values, start=2):
            if app_row[0] == telegram_id:
                applications.append(ApplicationResponse(
                    id=index,
                    telegram_id=app_row[0] if len(app_row) > 0 else None,
                    discord_id=app_row[1] if len(app_row) > 1 else None,
                    submitted_at=app_row[2] if len(app_row) > 2 else None,
                    updated_at=app_row[3] if len(app_row) > 3 else None,
                    email=app_row[4] if len(app_row) > 4 else None,
                    phone=app_row[5] if len(app_row) > 5 else None,
                    name=app_row[6] if len(app_row) > 6 else None,
                    surname=app_row[7] if len(app_row) > 7 else None,
                    patronymic=app_row[8] if len(app_row) > 8 else None,
                    university=app_row[9] if len(app_row) > 9 else None,
                    student_group=app_row[10] if len(app_row) > 10 else None,
                    applicant_role=app_row[11] if len(app_row) > 11 else None,
                    title=app_row[12] if len(app_row) > 12 else None,
                    adviser=app_row[13] if len(app_row) > 13 else None,
                    coauthors=[
                        Coauthor(
                            surname=coauthor.split()[0],
                            name=coauthor.split()[1],
                            patronymic=coauthor.split()[2]
                        ) for coauthor in app_row[14].split(", ") if coauthor
                    ] if len(app_row) > 14 else [],
                    conference_id=row[0]
                ))
    return applications
