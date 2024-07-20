import gspread
from helpers.config_helper import get_config

gs = gspread.service_account()


def get_sheet_by_id(sheet_id):
    return gs.open_by_key(sheet_id).sheet1


def get_authors_by_id(sheet_id):
    return gs.open_by_key(sheet_id).get_worksheet(1)

def get_conferences():
    # получение id конференции из config
    config = get_config()
    # открытие таблицы с информацией о конференциях
    sheet = gs.open_by_key(config['conferences-sheet-id']).sheet1
    # возвращаем строки с конференциями
    return sheet.get_all_records()

def get_conference_sheet_id(conference_id):
    # получение всех конференций
    records = get_conferences()
    # поиск требуемой строки по id конференции
    for record in records:
        if record['conference_id'] == conference_id:
            return record['sheet_id']
    return None




