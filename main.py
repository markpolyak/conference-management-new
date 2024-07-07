from fastapi import FastAPI, UploadFile, File
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
import io
from get_item import *
import logging

# Настройка журналирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Области доступа для учетных записей (google sheets и google drive)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# Загрузка учетных данных из файла сервисного аккаунта
# credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
credentials = service_account.Credentials.from_service_account_file('creds.json', scopes=scope)

# google drive folder id
folder_id = '1-501eVaZotRZneaIjwnvmuZ2Ry4p9Ljf'
# сервис для взаимодействия с google drive api
drive_service = build('drive', 'v3', credentials=credentials)
# авторизованный клиент для работы с google sheets
gc = gspread.authorize(credentials)


async def get_google_sheet_data(conference_id):
    table_key = get_participants_table_key_by_conference_id(conference_id)
    worksheet = gc.open_by_key(table_key).sheet1
    records = worksheet.get_all_records()
    return records


@app.get("/conferences/{conference_id}/publications")
async def get_publications(conference_id: int, email: str = None, telegram_id: str = None, discord_id: str = None):
    try:
        records = await get_google_sheet_data(conference_id)
        data = []
        if email:
            for record in records:
                if (record['email'] == email) & (record['upload_date'] != ''):
                    data.append({
                        'id': record['id'],
                        'publication_title': record['publication_title'],
                        'upload_date': record['upload_date'],
                        'review_status': record['review_status']
                    })
        elif telegram_id:
            for record in records:
                if (record['telegram_id'] == telegram_id) & (record['upload_date'] != ''):
                    data.append({
                        'id': record['id'],
                        'publication_title': record['publication_title'],
                        'upload_date': record['upload_date'],
                        'review_status': record['review_status']
                    })
        elif discord_id:
            for record in records:
                if (record['discord_id'] == discord_id) & (record['upload_date'] != ''):
                    data.append({
                        'id': record['id'],
                        'publication_title': record['publication_title'],
                        'upload_date': record['upload_date'],
                        'review_status': record['review_status']
                    })
        if data:
            return data
        else:
            raise HTTPException(status_code=404, detail="No publications found")
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 404:
            raise e
        logger.exception("Произошла ошибка при доступе к Google Sheets")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@app.get("/conferences/{conference_id}/applications/{application_id}/publication")
async def get_single_application(conference_id: int, application_id: int, email: str = None,
                                 telegram_id: str = None, discord_id: str = None):
    try:
        records = await get_google_sheet_data(conference_id)
        for record in records:
            if record['id'] == application_id:
                if (((email is not None) & (email == record['email'])) or
                        ((telegram_id is not None) & (telegram_id == record['telegram_id'])) or
                        ((discord_id is not None) & (discord_id == record['discord_id']))):
                    return {
                        'id': record['id'],
                        'publication_title': record['publication_title'],
                        'upload_date': record['upload_date'],
                        'review_status': record['review_status'],
                        'download_url': record['download_url'],
                        'keywords': record['keywords'],
                        'abstract': record['abstract']
                    }
                else:
                    raise HTTPException(status_code=403, detail="Wrong email/telegram/discord")
        raise HTTPException(status_code=404, detail="Publication not found")

    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 404:
            raise e
        elif isinstance(e, HTTPException) and e.status_code == 403:
            raise e
        logger.exception("Произошла ошибка при доступе к Google Sheets")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@app.post("/conferences/{conference_id}/applications/{application_id}/publication")
async def upload_application(conference_id: int, application_id: int, email: str = None,
                             telegram_id: str = None, discord_id: str = None,
                             file: UploadFile = File(...)):
    try:
        records = await get_google_sheet_data(conference_id)
        for record in records:
            if record['id'] == application_id:
                if (((email is not None) & (email == record['email'])) or
                        ((telegram_id is not None) & (telegram_id == record['telegram_id'])) or
                        ((discord_id is not None) & (discord_id == record['discord_id']))):
                    if file.filename == '':
                        raise HTTPException(status_code=400, detail="No selected file")
                    # Чтение содержимого файла
                    file_content = await file.read()

                    # Создание метаданных файла
                    file_metadata = {'name': file.filename, 'parents': [folder_id]}

                    # создается объект MediaIoBaseUpload, для загрузки содержимого файла на Google Drive
                    # преобразуется байтовое содержимое файла в поток, который может быть использован для загрузки
                    # указывается MIME-тип файла, (берется из загружаемого)
                    media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype=file.content_type)

                    # Загрузка файла на Google Drive
                    gfile = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                else:
                    raise HTTPException(status_code=403, detail="Wrong email/telegram/discord")
        raise HTTPException(status_code=404, detail="Publication not found")

    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == (404 or 403):
            raise e
        logger.exception("")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
