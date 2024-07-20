from pydantic import BaseModel
from typing import Optional


class ApplicationDelete(BaseModel):
    telegram_id: Optional[str] = None
    discord_id: Optional[str] = None
    email: Optional[str] = None