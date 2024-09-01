import os
import httplib2

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from configparser import ConfigParser
from dataclasses import dataclass
# from sheets.utils import get_fields


@dataclass
class ConferencesSheetConfig:
    id: str
    list: str
    sacc: None = None
    fields: None = None

    def __post_init__(self):
        creds_json  = os.path.dirname(__file__) + '/credentials.json'
        scopes = ['https://www.googleapis.com/auth/spreadsheets']

        try:
            creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
            self.sacc = build('sheets', 'v4', http=creds_service)

            r = self.sacc.spreadsheets().values().get(
                spreadsheetId=self.id,
                range=f'{self.list}!A1:P1'
            ).execute()
            values = r.get('values', [])
            if not values:
                raise Exception(f'{self.__class__.__name__} could not retrieve fields from the spreadsheet')

            self.fields = values[0]

        except Exception as e:
            print(f'config.setup: could not setup google service account: {e}')
            exit(1)


@dataclass
class FastApiConfig:
    host: str
    port: int

    def __post_init__(self):
        if self.port.isdigit():
            self.port = int(self.port)


def setup(section, filename='config.ini'):
    return_object = None
    parser = ConfigParser()
    parser.read(filename)

    if not section:
        raise Exception('Section you specified is invalid')

    if not parser.has_section(section):
        raise Exception(f'File {filename} does not have section {section}')

    if section == 'conferences sheets':
        return_object = ConferencesSheetConfig

    if section == 'fastapi':
        return_object = FastApiConfig

    if not os.path.isfile(filename):
        raise Exception('No config.ini file found')

    if not return_object:
        raise Exception('Could not set config instance')

    params = parser.items(section)

    try: 
        return return_object(**{i: k for i, k in params})

    except Exception as e:
        print(f'config.setup error: {e}')
        exit(1)

