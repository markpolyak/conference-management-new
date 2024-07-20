from pydantic import BaseModel
from typing import Optional


class ApplicationPatch(BaseModel):
    id: Optional[int] = None
    telegram_id: Optional[str] = None
    discord_id: Optional[str] = None
    submitted_at: Optional[str] = None
    updated_at: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    patronymic: Optional[str] = None
    university: Optional[str] = None
    student_group: Optional[str] = None
    applicant_role: Optional[str] = None
    title: Optional[str] = None
    adviser: Optional[str] = None
    coauthors: Optional[str] = None