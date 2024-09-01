from itertools import zip_longest
from . import models, utils, filters


def get_all(conf, filter_type='active'):
    r = conf.sacc.spreadsheets().values().get(
        spreadsheetId=conf.id,
        range=f'{conf.list}!A2:P'
    ).execute()
    if not r:
        return None

    values = r.get('values', [])
    if not values:
        return None

    conferences = []
    for conference_data in values:
        try:
            dict_data = dict(zip_longest(conf.fields, conference_data, fillvalue=''))
            utils.dict_string_to_datetime(dict_data, 'registration_start_date', 'registration_end_date')
            conferences.append(models.GetConferenceShort.model_validate(dict_data))

        except Exception as e:
            print(e)
            continue

    return filters.ConferencesFilter(filter_type, conferences).exec()


def get_by_id(conf, conference_id):
    r = conf.sacc.spreadsheets().values().get(
        spreadsheetId=conf.id,
        range=f'{conf.list}!A2:P'
    ).execute()
    if not r:
        print('sheets_ops.get_conference_by_id: Could not retrieve info from the spreadsheet')
        return None

    values = r.get('values', [])
    if not values:
        print('sheets_ops.get_conference_by_id: Values field is null in spreadsheet')
        return None

    conference_data = None
    for conference in values:
        if conference[0] == conference_id:
            conference_data = conference
            break

    if not conference_data:
        return None

    try:
        dict_data = dict(zip_longest(conf.fields, conference_data, fillvalue=''))
        return models.GetConference.model_validate(dict_data)

    except Exception as e:
        print(f'sheets_ops.get_conference_by_id: {e}')
        return None


def add(conf, model):
    lr = utils.get_last_empty_range(conf.sacc, conf.id, conf.list)
    if not lr:
        print('sheets_ops.add_conference: Could not retrieve last empty row from spreadsheet')
        return None

    body = {
        'values': [
            model.convert_for_spreadsheet()
        ]
    }

    r = conf.sacc.spreadsheets().values().append(
        spreadsheetId=conf.id,
        range=f'{conf.list}!B{lr}:P',
        valueInputOption='RAW',
        body=body
    ).execute()

    updates = r.get('updates', [])
    if not updates:
        print('sheets_ops.add_conference: Could not add conference to spreadsheet')
        return None

    if updates.get('updatedRows', 0) < 1:
        return None

    return model


def update(conf, conference_id, model):
    cr = utils.get_conference_row(conf.sacc, conf.id, conf.list, conference_id)
    if not cr:
        return -1

    body = {
        'values': [
            model.convert_for_spreadsheet()
        ]
    }

    r = conf.sacc.spreadsheets().values().update(
        spreadsheetId=conf.id,
        range=f'{conf.list}!B{cr}:P{cr}',
        valueInputOption='RAW',
        body=body
    ).execute()
    if not r:
        return None

    if r.get('updatedRows', 0) < 1:
        return None

    r = conf.sacc.spreadsheets().values().get(
        spreadsheetId=conf.id,
        range=f'{conf.list}!A{cr}:P{cr}'
    ).execute()

    conference_data = r.get('values', [])
    if not conference_data:
        return None

    try:
        dict_data = dict(zip_longest(conf.fields, conference_data[0], fillvalue=''))
        return models.UpdateConference.model_validate(dict_data)

    except Exception as e:
        print(e)
        return None
