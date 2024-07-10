import datetime

from fastapi import HTTPException
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def get_participants_table_key_by_conference_id(conference_id: int) -> str:
    try:
        # Определение области доступа и авторизация
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
        gc = gspread.authorize(credentials)

        # Открытие таблицы
        worksheet = gc.open_by_key('1a00wD6WggodhN3-OV1qQftzLZMvMHE_9RnM3ENZygLM').sheet1

        # Получение всех записей из таблицы
        records = worksheet.get_all_records()
        for record in records:
            if record['id'] == conference_id:
                if record['registration_end_date'] < datetime.datetime.now().astimezone().isoformat():
                    raise HTTPException(status_code=403, detail="Registration is closed")
                else:
                    return record['google_spreadsheet']

        raise HTTPException(status_code=404, detail="Conference not found")
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 404:
            raise e
        elif isinstance(e, HTTPException) and e.status_code == 403:
            raise e
        raise HTTPException(status_code=500, detail=f"Error accessing Google Sheets: {str(e)}")
