from pydantic import BaseModel

coathor_headers = ["name", "surname", "patronymic"]


class Coauthor(BaseModel):
    name: str
    surname: str
    patronymic: str
