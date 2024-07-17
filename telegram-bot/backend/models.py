from pydantic import BaseModel, EmailStr
from typing import List

class Conference(BaseModel):
    id: int
    sheet_id: str
    full_name: str
    short_name: str
    full_name_eng: str | None = None
    short_name_eng: str | None = None
    organization: str
    application_start: str
    application_end: str
    report_start: str
    report_end: str
    conference_start: str
    conference_end: str
    website: str | None = None
    contact_email: EmailStr
    google_spreadsheet: str | None = None

class Coauthor(BaseModel):
    name: str
    surname: str
    patronymic: str

class Application(BaseModel):
    id: int | None = None
    telegram_id: str | None = None
    discord_id: str | None = None
    submitted_at: str | None = None
    updated_at: str | None = None
    email: EmailStr
    phone: str | None = None
    name: str
    surname: str
    patronymic: str
    university: str
    student_group: str | None = None
    applicant_role: str
    title: str
    adviser: str
    coauthors: List[Coauthor] | None = []

class DeleteData(BaseModel):
    telegram_id: str | None = None
    discord_id: str | None = None
    email: str | None = None


