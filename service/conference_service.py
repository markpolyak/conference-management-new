import datetime
from fastapi import HTTPException
from gspread import Client
from datetime import datetime

import config

def get_info_by_conference_id(conference_id: int, sheets_service: Client):
    sheet = sheets_service.open_by_key(config.CONFERENCES_SPREADSHEET_ID).sheet1
    data = sheet.get_all_records()

    for row in data:
        if row["conference_id"] == conference_id:
            str_time = datetime.strptime(row["registration_end_date"], '%d.%m.%Y')
            if str_time >= datetime.now():
                return {
                    "spreadsheet_id": row["spreadsheet_id"],
                    "folder_id": row["folder_id"],
                    "registration_end_date": row["registration_end_date"]
                }
            else:
                raise HTTPException(403, "The registration time has passed")

    raise HTTPException(404, "Invalid conference id")