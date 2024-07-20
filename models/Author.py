from typing import Optional
from pydantic import BaseModel


class Author(BaseModel):
    id: int
    email: Optional[str]
    name: str
    surname: str
    patronymic: str
