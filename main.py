import datetime
import gspread
from pydantic import BaseModel, field_validator
from fastapi import FastAPI, status, Header, HTTPException
from dotenv import load_dotenv, find_dotenv
from os import getenv

load_dotenv(find_dotenv())

app = FastAPI()
account = gspread.service_account(filename=getenv("LOGIN_JSON"))

sheet = account.open_by_key(getenv("SHEET_ID"))
conf_page = sheet.sheet1
conference_head = [
    "google_spreadsheet",
    "name_rus",
    "name_rus_short",
    "name_eng",
    "name_eng_short",
    "registration_start_date",
    "registration_end_date",
    "submission_start_date",
    "submission_end_date",
    "conf_start_date",
    "conf_end_date",
    "organized_by",
    "url",
    "email",
    "gdrive_folder_id"
]


class ConfPut(BaseModel):
    google_spreadsheet: str | None = None
    name_rus: str | None = None
    name_rus_short: str | None = None
    name_eng: str | None = None
    name_eng_short: str | None = None
    registration_start_date: str | None = None
    registration_end_date: str | None = None
    submission_start_date: str | None = None
    submission_end_date: str | None = None
    conf_start_date: str | None = None
    conf_end_date: str | None = None
    organized_by: str | None = None
    url: str | None = None
    email: str | None = None
    gdrive_folder_id: str | None = None

    @field_validator('registration_start_date', 'registration_end_date', 'submission_start_date', 'submission_end_date',
                     'conf_start_date', 'conf_end_date')
    def validate_date(cls, value):
        try:
            datetime.datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError(f'Invalid date format for {value}. Should be dd.mm.yyyy')
        return value


class ConfPost(BaseModel):
    google_spreadsheet: str
    name_rus: str
    name_rus_short: str
    name_eng: str | None = None
    name_eng_short: str | None = None
    registration_start_date: str
    registration_end_date: str
    submission_start_date: str
    submission_end_date: str
    conf_start_date: str
    conf_end_date: str
    organized_by: str
    url: str| None = None
    email: str
    gdrive_folder_id: str| None = None

    @field_validator('registration_start_date', 'registration_end_date', 'submission_start_date', 'submission_end_date',
                     'conf_start_date', 'conf_end_date')
    def validate_date(cls, value):
        try:
            datetime.datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError(f'Invalid date format for {value}. Should be dd.mm.yyyy')
        return value


def verify_token(token):
    return token == getenv("BEARER_TOKEN")


def get_current_date():
    return datetime.datetime.now().strftime("%d.%m.%Y")


def compare_dates(date_str, start_date_str, end_date_str):
    current_date = datetime.datetime.strptime(date_str, "%d.%m.%Y")
    start_date = datetime.datetime.strptime(start_date_str, "%d.%m.%Y")
    end_date = datetime.datetime.strptime(end_date_str, "%d.%m.%Y")

    if start_date <= current_date <= end_date:
        return 0
    elif current_date < start_date:
        return 1
    else:
        return -1


def get_column_letter(column):
    column_letter = ""
    while column > 0:
        column_letter = chr((column - 1) % 26 + ord('A')) + column_letter
        column = (column - 1) // 26
    return column_letter


def get_record(record_id, page, head) -> dict | None:
    head_end_column = get_column_letter(len(head))
    data = page.get(range_name=f"A{record_id}:{head_end_column}{record_id}",
                    maintain_size=True, pad_values=True)[0]

    if all(element == '' for element in data):
        return None

    record = dict(zip(head, data))

    record["id"] = record_id

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
            return status.HTTP_400_BAD_REQUEST

    values = conf_page.get_all_values()

    for idx, row in enumerate(values, start=1):
        data_dictionary = dict(zip(conference_head, row))

        filtered_data = {k: data_dictionary[k] for k in fields}
        if compare(data_dictionary["registration_start_date"], data_dictionary["registration_end_date"]):
            filtered_data["id"] = idx
            conferences.append(filtered_data)
    return conferences


@app.get("/conferences/{conference_id}")
def get_conference(conference_id: int, authorization: str = Header(None)):
    authorized = False
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        if verify_token(token):
            authorized = True
        else:
            raise HTTPException(status_code=403, detail="Unauthorized access")

    conference = get_record(conference_id, conf_page, conference_head)
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    print(conference)
    if not authorized:
        conference.pop("google_spreadsheet")
    return conference


@app.post("/conferences")
def post_conferences(conf: ConfPost, authorization: str = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        if not verify_token(token):
            raise HTTPException(status_code=403, detail="Unauthorized access")
    else:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    conference_data = list(conf.model_dump().values())
    conf_page.append_row(conference_data, table_range="A1")
    new_conference_data = conf.dict()
    new_conference_data["id"] = len(conf_page.get_all_values())

    return new_conference_data


@app.put("/conferences/{conference_id}")
def put_conference(conference_id: int, change: ConfPut, authorization: str = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        if not verify_token(token):
            raise HTTPException(status_code=403, detail="Unauthorized access")
    else:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    conference = get_record(conference_id, conf_page, conference_head)
    if not conference:
        return status.HTTP_404_NOT_FOUND

    for (key, value) in change.dict().items():
        if value is not None and conference[key] is not None:
            conference[key] = value

    conference.pop("id")

    conf_page.batch_update(
        [{'range': f"A{conference_id}:{get_column_letter(len(conference))}{conference_id}",
          'values': [list(conference.values())]}])

    conference["id"] = conference_id

    return conference

