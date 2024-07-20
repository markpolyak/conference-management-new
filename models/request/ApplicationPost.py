from pydantic import BaseModel
from typing import Optional, List


class ApplicationPost(BaseModel):
    id: Optional[int] = None
    telegram_id: Optional[str] = None
    discord_id: Optional[str] = None
    submitted_at: Optional[str] = None
    updated_at: Optional[str] = None
    email: str
    phone: Optional[str] = None
    name: str
    surname: str
    patronymic: str
    university: str
    student_group: Optional[str] = None
    applicant_role: str
    title: str
    adviser: str
    coauthors: Optional[List] = None
