from pydantic import BaseModel, field_validator
from datetime import datetime

conference_head = [
    "spreadsheet_id",
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
    spreadsheet_id: str | None = None
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

    @classmethod
    @field_validator('registration_start_date', 'registration_end_date', 'submission_start_date', 'submission_end_date',
                     'conf_start_date', 'conf_end_date',)
    def validate_date(cls, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError(f'Invalid date format for {value}. Should be dd.mm.yyyy')
        return value


class ConfPost(BaseModel):
    spreadsheet_id: str
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
    url: str | None = None
    email: str
    gdrive_folder_id: str | None = None

    @field_validator('registration_start_date', 'registration_end_date', 'submission_start_date', 'submission_end_date',
                     'conf_start_date', 'conf_end_date')
    def validate_date(cls, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError(f'Invalid date format for {value}. Should be dd.mm.yyyy')
        return value
