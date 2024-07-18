import os.path
from Article import Article
from Author import Author

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import spreadsheet_id


class ConferenceTable:  # схема столбцов таблицы
    id_column: int
    name_column: int
    surname_column: int
    patronymic_column: int
    student_group_column: int
    applicant_role_column: int
    title_column: int
    presentation_quality_column: int
    advisor_confirmation_column: int

    def get_table_scheme(self, column_names):   # получаем схему столбцов таблицы
        self.id_column = column_names.index("id")
        self.name_column = column_names.index("name")
        self.surname_column = column_names.index("surname")
        self.patronymic_column = column_names.index("patronymic")
        self.student_group_column = column_names.index("student_group")
        self.applicant_role_column = column_names.index("applicant_role")
        self.title_column = column_names.index("title")
        self.presentation_quality_column = column_names.index("presentation_quality")
        self.advisor_confirmation_column = column_names.index("advisor_confirmation")


def get_credentials():  # для создания файла с токеном и получения credentials для работы с таблицами
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def reformate(sheet_values, table_scheme):  # приводим данные из таблицы к более удобному виду
    values = []
    for row in sheet_values:
        if len(row)-1 < table_scheme.advisor_confirmation_column:
            advisor_confirmation = 0
        else:
            advisor_confirmation = row[table_scheme.advisor_confirmation_column]
        author = Author(surname=row[table_scheme.surname_column],
                        name=row[table_scheme.name_column],
                        patronymic=row[table_scheme.patronymic_column],
                        group=row[table_scheme.student_group_column])
        article = Article(author=author, title=row[table_scheme.title_column],
                          presentation_quality=row[table_scheme.presentation_quality_column],
                          advisor_confirmation=advisor_confirmation)
        values.append(article)
    return values   #


def get_spreadsheet_id(conference_id):  # из таблицы с конференциями по id конференции получаем id гугл таблицы
    creds = get_credentials()
    range_name = "Конференции!A:O"
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name,
                                majorDimension="COLUMNS").execute()
    sheet_values = result.get("values", [])
    for item in sheet_values:
        if item[0] == "spreadsheet_id":  # ищем столбец с id таблиц
            if len(item)-1 >= conference_id:
                if item[conference_id] == "":
                    return "Not found"  # если ячейка пуста, то возвращаем "Not found"
                return item[conference_id]
            else:
                return "Not found"  # если conference_id больше, чем количество конференций, то возвращаем "Not found"
    return "Not found"  # если в таблице нет столбца spreadsheet_id, то возвращаем "Not found"


def get_conference_name(conference_id):
    creds = get_credentials()
    range_name = "Конференции!A:O"
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name,
                                majorDimension="COLUMNS").execute()
    sheet_values = result.get("values", [])
    for item in sheet_values:
        if item[0] == "name_rus_short":  # ищем столбец с названиями конференций
            if len(item)-1 >= conference_id:
                if item[conference_id] == "":
                    return "Not found"  # если ячейка пуста, то возвращаем "Not found"
                return item[conference_id]
            else:
                return "Not found"  # если conference_id больше, чем количество конференций, то возвращаем "Not found"
    return "Not found"  # если в таблице нет столбца name_rus_short, то возвращаем "Not found"


def get_sheet_values(creds, spreadsheet_id):    # получаем данные из таблицы с заявками
    range_name = "Заявки!A:S"
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name,
                                majorDimension="ROWS").execute()
    sheet_values = result.get("values", [])

    table_scheme = ConferenceTable()
    table_scheme.get_table_scheme(sheet_values[0])  # по заголовкам столбцов получаем схему таблицы

    values = reformate(sheet_values[1:], table_scheme)  # преобразуем данные из столбцов в удобный вид
    return values
