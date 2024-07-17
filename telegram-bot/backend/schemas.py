from pydantic import BaseModel, EmailStr
from typing import List
from .models import Coauthor

class ConferenceResponse(BaseModel):
    id: int
    name_rus_short: str
    name_eng_short: str | None = None
    conf_start_date: str
    conf_end_date: str

class ApplicationResponse(BaseModel):
    id: int
    telegram_id: str | None = None
    discord_id: str | None = None
    submitted_at: str
    updated_at: str
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
    conference_id: int | None = None
