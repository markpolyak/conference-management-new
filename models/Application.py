from models.Coauthor import *

application_headers = [
    "telegram_id", "discord_id", "submitted_at", "updated_at", "email",
    "phone", "name", "surname", "patronymic", "university", "student_group",
    "applicant_role", "title", "adviser"
]
class Application(BaseModel):
    telegram_id: str | None
    discord_id: str | None
    submitted_at: str | None
    updated_at: str | None
    email: str
    phone: str | None
    name: str
    surname: str
    patronymic: str | None
    university: str
    student_group: str | None
    applicant_role: str
    title: str
    adviser: str | None
    coauthors: list[Coauthor] | None = []


class ApplicationPatch(BaseModel):
    telegram_id: str | None = None
    discord_id: str | None = None
    email: str | None = None
    phone: str | None = None
    name: str | None = None
    surname: str | None = None
    patronymic: str | None = None
    university: str | None = None
    student_group: str | None = None
    applicant_role: str | None = None
    title: str | None = None
    adviser: str | None = None
    coauthors: list[Coauthor] | None = []


class DeleteRequest(BaseModel):
    telegram_id: str | None = None
    discord_id: str | None = None
    email: str | None = None