import datetime
from datetime import datetime
from fastapi import HTTPException


def get_participants_table_key_by_conference_id(conference_id: int, gc):
    try:
        # Определение области доступа и авторизация
        # scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        # credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
        # gc = gspread.authorize(credentials)

        # Открытие таблицы
        worksheet = gc.open_by_key('1a00wD6WggodhN3-OV1qQftzLZMvMHE_9RnM3ENZygLM').sheet1

        # Получение всех записей из таблицы
        records = worksheet.get_all_records()
        for record in records:
            if record['conference_id'] == conference_id:
                date_str = record['registration_end_date']
                date_obj = datetime.strptime(date_str, '%d.%m.%Y')
                iso_format_date = date_obj.isoformat()
                if iso_format_date < datetime.now().astimezone().isoformat():
                    raise HTTPException(status_code=403, detail="Registration is closed")
                else:
                    return [record['spreadsheet_id'], record['gdrive_folder_id'], iso_format_date]

        raise HTTPException(status_code=404, detail="Conference not found")
    except Exception as e:
        raise e
