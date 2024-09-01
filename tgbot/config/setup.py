import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from configparser import ConfigParser
from dataclasses import dataclass, field


@dataclass
class TelegramConfig:
    token: str


@dataclass
class BackendConfig:
    uri: str
    get_uri: str = field(init=False)
    post_uri: str = field(init=False)
    put_uri: str = field(init=False)

    def __post_init__(self):
        self.get_uri = f'http://{self.uri}/conferences'
        self.get_single_uri = f'http://{self.uri}/conferences/'
        self.post_uri = f'http://{self.uri}/conferences'
        self.put_uri = f'http://{self.uri}/conferences/'


@dataclass
class Database:
    filename: str
    table: str


@dataclass
class GoogleDrive:
    sacc: None = None

    def __post_init__(self):
        scopes = ['https://www.googleapis.com/auth/drive.metadata.readonly']
        creds_json  = os.path.dirname(__file__) + '/credentials.json'

        try:
            creds = service_account.Credentials.from_service_account_file(creds_json, scopes=scopes)
            self.sacc = build('drive', 'v3', credentials=creds)

        except Exception as e:
            print(f'config.setup: could not setup google service account: {e}')
            exit(1)


def setup(section, filename='config.ini'):
    return_object = None
    parser = ConfigParser()
    parser.read(filename)

    if not section:
        raise Exception('Section you specified is invalid')

    if not parser.has_section(section) and section != 'google drive':
        raise Exception(f'File {filename} does not have section {section}')

    if section == 'telegram bot':
        return_object = TelegramConfig

    if section == 'backend':
        return_object = BackendConfig

    if section == 'database':
        return_object = Database

    if section == 'google drive':
        # return_object = GoogleDrive
        return GoogleDrive()

    if not os.path.isfile(filename):
        raise Exception('No config.ini file found')

    if not return_object:
        raise Exception('Could not set config instance')

    params = parser.items(section)

    try: 
        return return_object(**{i: k for i, k in params})

    except Exception as e:
        print(e)
        exit(1)
