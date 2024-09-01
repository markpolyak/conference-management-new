from pydantic import BaseModel, Field, EmailStr, field_validator, field_serializer
from datetime import datetime
from typing import Optional


class Conference(BaseModel):
    id: str
    google_spreadsheet: str
    google_drive_directory_id: str
    name_rus: str
    name_rus_short: str
    name_eng: Optional[str] = ''
    name_eng_short: Optional[str] = ''
    organized_by: str
    registration_start_date: str
    registration_end_date: str
    submission_start_date: str
    submission_end_date: str
    conf_start_date: str
    conf_end_date: str
    url: Optional[str] = ''
    email: EmailStr

    @field_validator(
            'registration_start_date',
            'registration_end_date',
            'submission_start_date',
            'submission_end_date',
            'conf_start_date',
            'conf_end_date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%d.%m.%Y')
        except ValueError:
            raise ValueError('Incorrect date format, must be %d.%m.%Y')
        return v

    @field_serializer(
        'id'
    )
    def convert_to_int(v):
        try:
            return int(v)
        except Exception as e:
            print(e)
            return v

    def convert_for_spreadsheet(self):
        return list(self.model_dump().values())


class PostConference(Conference):
    id: str = Field(default=0, exclude=True)


class GetConference(Conference):
    id: str
    google_spreadsheet: str = Field(default='', exclude=True)


class GetConferenceShort(Conference):
    id: str
    name_rus: str = Field(exclude=True)
    name_eng: str = Field(exclude=True)
    google_spreadsheet: str = Field(exclude=True)
    google_drive_directory_id: str = Field(exclude=True)
    organized_by: str = Field(exclude=True)
    registration_start_date: datetime = Field(exclude=True)
    registration_end_date: datetime = Field(exclude=True)
    submission_start_date: str = Field(exclude=True)
    submission_end_date: str = Field(exclude=True)
    url: str = Field(exclude=True)
    email: EmailStr = Field(exclude=True)

    @field_validator(
        'registration_start_date',
        'registration_end_date',
    )
    def validate_date(cls, v):
        return v


class UpdateConference(Conference):
    id: int = Field(default=0, exclude=True)
