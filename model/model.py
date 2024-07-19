from typing import Union
from fastapi import Form
from pydantic import BaseModel

class Publication(BaseModel):
    email: Union[str, None] = None
    telegram_id: Union[str, None] = None
    discord_id: Union[str, None] = None
    publication_title: str
    keywords: Union[str, None] = None
    abstract: Union[str, None] = None

class MetaData(BaseModel):
    email: Union[str, None] = None
    telegram_id: Union[str, None] = None
    discord_id: Union[str, None] = None
    publication_title: Union[str, None] = None
    keywords: Union[str, None] = None
    abstract: Union[str, None] = None

async def get_form_data_publication(
    email: str = Form(None), telegram_id: str = Form(None), discord_id: str = Form(None),
    publication_title: str = Form(...), keywords: str = Form(None), abstract: str = Form(None)
) -> Publication:
    return Publication(email=email, telegram_id=telegram_id, discord_id=discord_id,
                       publication_title=publication_title, keywords=keywords, abstract=abstract)

async def get_form_meta_data(
    email: str = Form(None), telegram_id: str = Form(None), discord_id: str = Form(None),
    publication_title: str = Form(None), keywords: str = Form(None), abstract: str = Form(None)
) -> MetaData:
    return MetaData(email=email, telegram_id=telegram_id, discord_id=discord_id,
                    publication_title=publication_title, keywords=keywords, abstract=abstract)