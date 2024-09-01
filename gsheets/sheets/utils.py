from datetime import datetime


def dict_string_to_datetime(d, *keys):
    for key in keys:
        try:
            dtime = datetime.strptime(d[key], '%d.%m.%Y')
        except Exception as e:
            print(e)
            dtime = datetime.strptime(d[key])
        d.update({key: dtime})


def get_last_empty_range(sacc, spreadsheet_id, spreadsheet_list):
    r = sacc.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f'{spreadsheet_list}!A2:A'
    ).execute()
    values = r.get('values', [])
    if not values:
        return 2

    try:
        return int(values[-1][0]) + 2

    except Exception as e:
        print(e)
        return None


def get_conference_row(sacc, spreadsheet_id, spreadsheet_list, conf_id):
    r = sacc.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f'{spreadsheet_list}!A2:P'
    ).execute()
    values = r.get('values', [])
    if not values:
        return 2

    ids = [i[0] for i in values if len(i) > 1]
    if not conf_id in ids:
        return None

    try:
        return int(conf_id) + 1

    except Exception as e:
        print(e)
        return None
