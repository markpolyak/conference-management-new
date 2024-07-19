import os
import re
import traceback
from datetime import datetime

import gspread
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from model.model import Publication, get_form_data_publication, MetaData, get_form_meta_data
from service.conference_service import get_info_by_conference_id
from service.google_drive_service import upload_file

load_dotenv()
app = FastAPI()

gspread_client = gspread.oauth()

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

def check_user_id(telegram_id: str = None, discord_id: str = None, email: str = None):
    variables = {
        "telegram_id": telegram_id,
        "discord_id": discord_id,
        "email": email
    }

    result = {}

    for key, value in variables.items():
        if value is not None:
            result[key] = value

    if(len(result) == 1):
        first_key = next(iter(result))
        return first_key, result[first_key]
    else:
        raise HTTPException(403, "Только одно из полей: telegram_id, discord_id, email не должно быть пустым")

def update_cells(publication_info: dict, conference_id: int):
    info = get_info_by_conference_id(conference_id, gspread_client)
    publications_sheet = gspread_client.open_by_key(info["spreadsheet_id"]).sheet1

    headers = publications_sheet.row_values(1)

    for key, value in publication_info.items():
        publications_sheet.update_cell(publication_info["id"] + 1, headers.index(key) + 1, value)

def get_publications_by_conference_id(conference_id: int):
    info = get_info_by_conference_id(conference_id, gspread_client)
    publications_sheet = gspread_client.open_by_key(info["spreadsheet_id"])
    return publications_sheet.sheet1.get_all_records()

@app.get("/conferences/{conference_id}/publications")
async def get_publications(conference_id: int, telegram_id: str = None,
                           discord_id: str = None, email: str = None):
    print(os.getenv("CONFERENCES_SPREADSHEET_ID"))
    try:
        user_id_key, user_id_value = check_user_id(telegram_id, discord_id, email)
        records = get_publications_by_conference_id(conference_id)

        result = []

        for record in records:
            if (str(record[user_id_key]) == user_id_value) & (record["upload_date"] != ""):
                result.append({
                    "id": record["id"],
                    "title": record["title"],
                    "upload_date": record["upload_date"],
                    "review_status": record["review_status"]
                })

        if len(result) != 0:
            return result
        else:
            raise HTTPException(404, "Неправильный идентификатор пользователя: не было найдено публикаций.")
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(500, "Внутренняя ошибка сервера.")

@app.get("/conferences/{conference_id}/applications/{application_id}/publication")
async def get_publication(conference_id: int, application_id: int, telegram_id: str = None,
                          discord_id: str = None, email: str = None):
    try:
        user_id_key, user_id_value = check_user_id(telegram_id, discord_id, email)
        records = get_publications_by_conference_id(conference_id)

        for record in records:
            if record["id"] == application_id:
                if str(record[user_id_key]) == user_id_value:
                    return {
                        "id": record["id"],
                        "title": record["title"],
                        "upload_date": record["upload_date"],
                        "review_status": record["review_status"],
                        "download_url": record["download_url"],
                        "keywords": record["keywords"],
                        "abstract": record["abstract"]
                    }
                else:
                    raise HTTPException(403, "Неправильный идентификатор пользователя: публикация была загружена другим пользователем.")

        raise HTTPException(404, "Неправильный идентификатор заявки.")
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(500, "Внутренняя ошибка сервера.")

@app.post("/conferences/{conference_id}/applications/{application_id}/publication")
async def add_publication(conference_id: int, application_id: int,
                          publication: Publication = Depends(get_form_data_publication),
                          file: UploadFile = File(...)):
    try:
        user_id_key, user_id_value = check_user_id(publication.telegram_id, publication.discord_id, publication.email)
        records = get_publications_by_conference_id(conference_id)

        publication_info = {}

        for record in records:
            if record["id"] == application_id:
                if record["upload_date"] == "":
                    if str(record[user_id_key]) == user_id_value:
                        publication_info = {
                            "id": record["id"],
                        }
                    else:
                        raise HTTPException(403, "Неправильный идентификатор пользователя: публикация была загружена другим пользователем.")
                else:
                    raise HTTPException(403, "Публикация уже была загружена, используйте метод put для изменения документа публикации.")

        if len(publication_info) == 0:
            raise HTTPException(404, "Нерпвильный идентификатор заявки.")

        link = await upload_file(drive, file, get_info_by_conference_id(conference_id, gspread_client)["folder_id"])

        publication_info["upload_date"] = datetime.now().astimezone().isoformat()
        publication_info["title"] = publication.publication_title
        publication_info["download_url"] = link
        publication_info["review_status"] = "in progress"

        if publication.abstract:
            publication_info["abstract"] = publication.abstract

        if publication.keywords:
            publication_info["keywords"] = publication.keywords

        update_cells(publication_info, conference_id)

        return publication_info
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(500, "Внутренняя ошибка сервера.")

@app.put("/conferences/{conference_id}/applications/{application_id}/publication")
async def update_publication(conference_id: int, application_id: int,
                             telegram_id: str = Form(None), discord_id: str = Form(None), email: str = Form(None),
                             file: UploadFile = File(...)):
    try:
        user_id_key, user_id_value = check_user_id(telegram_id, discord_id, email)
        records = get_publications_by_conference_id(conference_id)

        publication_info = {}

        for record in records:
            if record["id"] == application_id:
                if record["upload_date"] != "":
                    if str(record[user_id_key]) == user_id_value:
                        publication_info = {
                            "id": record["id"],
                            "download_url": record["download_url"],
                            "title": record["title"],
                            "keywords": record["keywords"],
                            "abstract": record["abstract"]
                        }
                    else:
                        raise HTTPException(403, "Неправильный идентификатор пользователя: публикация была загружена другим пользователем.")
                else:
                    raise HTTPException(400, "Документ публикации еще не был выложен, используйте метод post для добавления документа.")
        if len(publication_info) == 0:
            raise HTTPException(404, "Неправильный идентификатор заявки.")

        if publication_info["download_url"]:
            pattern = r'id=([^&]+)'
            match = re.search(pattern, publication_info["download_url"])

            if match:
                print(match.group(1))
                file_to_delete = drive.CreateFile({'id': match.group(1)})
                file_to_delete.Delete()


        link = await upload_file(drive, file, get_info_by_conference_id(conference_id, gspread_client)["folder_id"])

        publication_info["upload_date"] = datetime.now().astimezone().isoformat()
        publication_info["download_url"] = link
        publication_info["review_status"] = "in progress"

        update_cells(publication_info, conference_id)

        return publication_info
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(500, "Внутренняя ошибка сервера.")

@app.patch("/conferences/{conference_id}/applications/{application_id}/publication")
async def update_meta_data(conference_id: int, application_id: int,
                           meta_data: MetaData = Depends(get_form_meta_data)):
    try:
        user_id_key, user_id_value = check_user_id(meta_data.telegram_id, meta_data.discord_id, meta_data.email)
        records = get_publications_by_conference_id(conference_id)

        publication_info = {}

        for record in records:
            if record["id"] == application_id:
                if str(record[user_id_key]) == user_id_value:
                    publication_info = {
                        "id": record["id"],
                        "title": record["title"],
                        "upload_date": record["upload_date"],
                        "review_status": record["review_status"],
                        "download_url": record["download_url"],
                        "keywords": record["keywords"],
                        "abstract": record["abstract"]
                    }
                else:
                    raise HTTPException(403, "Неправильный идентификатор пользователя: публикация была загружена другим пользователем.")

        if len(publication_info) == 0:
            raise HTTPException(404, "Неправильный идентификатор заяки.")

        if meta_data.abstract:
            publication_info["abstract"] = meta_data.abstract

        if meta_data.publication_title:
            publication_info["title"] = meta_data.publication_title

        if meta_data.keywords:
            publication_info["keywords"] = meta_data.keywords

        update_cells(publication_info, conference_id)

        return publication_info
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(500, "Внутренняя ошибка сервера.")