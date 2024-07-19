import smtplib
import datetime
from email.mime.text import MIMEText

import gspread
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import HTTPBearer
from dotenv import load_dotenv, find_dotenv
from os import getenv

from gspread import Worksheet

from models.Conf import conference_head, ConfPut, ConfPost
from models.Application import *
from models.Coauthor import *

load_dotenv(find_dotenv())

app = FastAPI()
security = HTTPBearer(auto_error=False)
account = gspread.service_account(filename=getenv("LOGIN_JSON"))

sheet = account.open_by_key(getenv("SHEET_ID"))
conf_page = sheet.sheet1


def verify_token(token) -> bool:
    return token == getenv("BEARER_TOKEN")


def get_current_date() -> str:
    return datetime.datetime.now().strftime("%d.%m.%Y")


def compare_dates(date: str, start_date: str, end_date: str) -> int:
    current_date = datetime.datetime.strptime(date, "%d.%m.%Y")
    start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y")
    end_date = datetime.datetime.strptime(end_date, "%d.%m.%Y")

    if start_date <= current_date <= end_date:
        return 0
    elif current_date < start_date:
        return 1
    else:
        return -1


def get_column_letter(column: int) -> str:
    column_letter = ""
    while column > 0:
        column_letter = chr((column - 1) % 26 + ord('A')) + column_letter
        column = (column - 1) // 26
    return column_letter


def get_conference_record(record_id: int) -> dict | None:
    head = conference_head
    head_end_column = get_column_letter(len(head))
    data = conf_page.get(range_name=f"A{record_id}:{head_end_column}{record_id}",
                         maintain_size=True, pad_values=True)[0]

    if all(element == '' for element in data):
        return None

    record = dict(zip(head, data))

    record["conference_id"] = record_id

    return record


@app.get("/conferences")
def get_conferences(filter: str | None = None):
    conferences = []
    fields = ["name_rus_short", "name_eng_short", "conf_start_date", "conf_end_date"]
    match filter:
        case "all":
            compare = lambda a, b: True
        case "past":
            compare = lambda a, b: compare_dates(get_current_date(), a, b) == -1
        case "future":
            compare = lambda a, b: compare_dates(get_current_date(), a, b) == 1
        case "active" | None:
            compare = lambda a, b: compare_dates(get_current_date(), a, b) == 0
        case _:
            return HTTPException(status_code=400)

    values = conf_page.get_all_values()

    for idx, row in enumerate(values, start=1):
        data_dictionary = dict(zip(conference_head, row))

        filtered_data = {k: data_dictionary[k] for k in fields}
        if compare(data_dictionary["registration_start_date"], data_dictionary["registration_end_date"]):
            filtered_data["spreadsheet_id"] = idx
            conferences.append(filtered_data)
    return conferences


@app.get("/conferences/{conference_id}")
def get_conference(conference_id: int, authorization=Depends(security)):
    authorized = False
    if authorization:
        token = authorization.credentials
        if verify_token(token):
            authorized = True
        else:
            raise HTTPException(status_code=403, detail="Unauthorized access")

    conference = get_conference_record(conference_id)
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    if not authorized:
        conference.pop("spreadsheet_id")
    return conference


@app.post("/conferences")
def post_conferences(conf: ConfPost, authorization=Depends(security)):

    if authorization:
        token = authorization.credentials
        if not verify_token(token):
            raise HTTPException(status_code=403, detail="Unauthorized access")
    else:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    conference_data = list(conf.model_dump().values())
    conf_page.append_row(conference_data, table_range="A1")
    new_conference_data = conf.dict()
    new_conference_data["conference_id"] = len(conf_page.get_all_values())

    return new_conference_data


@app.put("/conferences/{conference_id}")
def put_conference(conference_id: int, change: ConfPut, authorization=Depends(security)):
    if authorization:
        token = authorization.credentials
        if not verify_token(token):
            raise HTTPException(status_code=403, detail="Unauthorized access")
    else:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    conference = get_conference_record(conference_id)
    if not conference:
        return status.HTTP_404_NOT_FOUND

    for (key, value) in change.model_dump().items():
        if value is not None and conference[key] is not None:
            conference[key] = value

    conference.pop("conference_id")

    conf_page.batch_update(
        [{'range': f"A{conference_id}:{get_column_letter(len(conference))}{conference_id}",
          'values': [list(conference.values())]}])

    conference["conference_id"] = conference_id

    return conference


# -----------------------------------------------------------------------------


def construct_application_dict(row: list, idx: int, author_page: Worksheet | None = None) -> dict | None:
    if not row:
        return None
    application = dict(zip(application_headers, row))
    application["id"] = idx
    coauthors = []
    if author_page:
        author_data = author_page.get_all_values()
        for coauthor_row in author_data:
            coauthor = dict(zip(["id"] + coathor_headers, coauthor_row))
            if coauthor["id"] == str(application["id"]) and \
                    not all(coauthor.get(key) == application.get(key) for key in coathor_headers):
                coauthor.pop("id")
                coauthors.append(coauthor)

    application["coauthors"] = coauthors
    return application


def serialize_application_to_list(appl_original: dict) -> (list, list):
    application = appl_original.copy()
    coauthors = application.pop("coauthors", [])
    idx = application.pop("id", None)
    application_list = list(application.values())

    coauthor_list = [[idx] + [application.get(key) for key in coathor_headers]]

    coauthor_list.extend([[idx] + [coauthor.get(key) for key in coathor_headers] for coauthor in coauthors])

    return application_list, coauthor_list


def send_delete_email(author_id, recipients, application_id, conference_id):
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        now = datetime.datetime.now().astimezone().strftime("%d.%m.%Y %H:%M:%S")
        email_text = (getenv("DELETE_MESSAGE_TEXT").format(author_id, now, application_id, conference_id))
        msg = MIMEText(email_text)
        msg["Subject"] = getenv("DELETE_MESSAGE_SUBJECT")
        msg["To"] = recipients
        msg["From"] = f"{getenv('GMAIL')}"
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(getenv("GMAIL"), getenv("GMAIL_PASS"))
        smtp_server.sendmail(msg["From"], recipients, msg.as_string())
        smtp_server.quit()


def patch_authors_page(page, idx, new_authors):
    old_authors = page.get_all_values()
    updated_authors = [author for author in old_authors if author[0] != str(idx)]
    updated_authors.extend(new_authors)
    page.clear()
    page.update('A1', updated_authors)


@app.post("/conferences/{conference_id}/applications")
def add_application(conference_id: int, application: Application):
    sheet_id = get_conference_record(conference_id)["spreadsheet_id"]
    app_page = account.open_by_key(sheet_id).worksheet(getenv("APPLICATION_TITLE"))
    author_page = account.open_by_key(sheet_id).worksheet(getenv("AUTHOR_TITLE"))

    new_application = application.model_dump()

    now = datetime.datetime.now().astimezone().isoformat()
    new_application.update({"submitted_at": now, "updated_at": now})
    data = app_page.get_all_values()
    new_application["id"] = len(data) + 1 if data != [[]] else 1

    appl, coathors = serialize_application_to_list(new_application)

    app_page.append_row(appl)
    for coauthor in coathors:
        author_page.append_row(coauthor)
    return new_application


@app.get("/conferences/{conference_id}/applications")
def get_applications(conference_id: int, email: str | None = None, telegram_id: str | None = None,
                     discord_id: str | None = None):
    if sum([bool(email), bool(telegram_id), bool(discord_id)]) != 1:
        raise HTTPException(status_code=400,
                            detail="Exactly one of 'email', 'telegram_id' or 'discord_id' must be provided")
    applications = []
    sheet_id = get_conference_record(conference_id)["spreadsheet_id"]
    app_page = account.open_by_key(sheet_id).worksheet(getenv("APPLICATION_TITLE"))
    author_page = account.open_by_key(sheet_id).worksheet(getenv("AUTHOR_TITLE"))

    app_data = app_page.get_values()
    for idx, row in enumerate(app_data, start=1):

        # record = make_application_record(row, idx)
        record = dict(zip(application_headers, row))
        record = construct_application_dict(row, idx, author_page)
        print(record)
        if record:
            if (email and record['email'] == email) or (
                    telegram_id and record['telegram_id'] == telegram_id) or (
                    discord_id and record['discord_id'] == discord_id):
                applications.append(record)

    if not applications:
        raise HTTPException(status_code=404, detail="No applications found")
    return applications


@app.patch("/conferences/{conference_id}/applications/{application_id}")
def edit_application(conference_id: int, application_id: int, application: ApplicationPatch):
    sheet_id = get_conference_record(conference_id)["spreadsheet_id"]
    app_page = account.open_by_key(sheet_id).worksheet(getenv("APPLICATION_TITLE"))
    author_page = account.open_by_key(sheet_id).worksheet(getenv("AUTHOR_TITLE"))

    data = app_page.row_values(application_id)
    existing_app = construct_application_dict(data, application_id, author_page)

    if not existing_app:
        raise HTTPException(status_code=404, detail="Application not found")

    if (application.telegram_id and existing_app['telegram_id'] != application.telegram_id) or \
            (application.discord_id and existing_app['discord_id'] != application.discord_id):
        raise HTTPException(status_code=403, detail="telegram_id or discord_id mismatch")

    for (key, value) in application.model_dump().items():
        if value is not None and key not in ['telegram_id', 'discord_id']:
            existing_app[key] = value

    existing_app["updated_at"] = datetime.datetime.now().astimezone().isoformat()

    new_application, new_coathors = serialize_application_to_list(existing_app)

    if application.coauthors:
        patch_authors_page(author_page, application_id, new_coathors)

    app_page.update([new_application],
                    f"A{application_id}:{get_column_letter(len(application_headers))}{application_id}")

    return existing_app


@app.delete("/conferences/{conference_id}/applications/{application_id}")
def delete_application(conference_id: int, application_id: int, delete_request: DeleteRequest):
    sheet_id = get_conference_record(conference_id)["spreadsheet_id"]
    app_page = account.open_by_key(sheet_id).worksheet(getenv("APPLICATION_TITLE"))

    data = app_page.row_values(application_id)
    existing_app = construct_application_dict(data, application_id)
    if not existing_app:
        raise HTTPException(status_code=404, detail="Application not found")

    if (delete_request.telegram_id and existing_app['telegram_id'] != delete_request.telegram_id) or \
            (delete_request.discord_id and existing_app['discord_id'] != delete_request.discord_id) or \
            (delete_request.email and existing_app['email'] != delete_request.email):
        raise HTTPException(status_code=404, detail="Application not found")
    conference = get_conference_record(conference_id)

    send_delete_email(existing_app["email"], conference["email"], application_id, conference_id)
    return {"message": "Для отмены заявки на участие в конференции свяжитесь с организаторами"}
