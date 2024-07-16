from pprint import pprint
from typing import Literal, Optional, TypedDict
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time
import ast
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

class TimeDict(TypedDict):
    day: str
    time: str

class SheetsController:

    def __init__(self, SPREADSHEET_ID: str) -> None:
        self.SPREADSHEET_ID = SPREADSHEET_ID

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            "creds.json",
            [
                ' https://www.googleapis.com/auth/spreadsheets ',
                ' https://www.googleapis.com/auth/drive ',
            ]
        )

        httpAuth = credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

    def get_value(self, range: str, majorDimension: Literal["ROWS", "COLUMNS"], sheetId: Optional[str]=None):
        values = self.service.spreadsheets().values().get(
            spreadsheetId=sheetId if sheetId else self.SPREADSHEET_ID,
            range=range,
            majorDimension=majorDimension,
        ).execute()

        try:
            return values["values"]
        except Exception as e:
            return [[""]]
 
    
    def get_all_values(self, majorDimension: Literal["ROWS", "COLUMNS"], sheet: Optional[Literal["ORGANIZATIONS", "USERS", "CONFERENCES", "USER_STATES"]]=None, sheetId: Optional[str]=None):

        range = f"'{sheet}'!1:1000" if sheet else "1:1000"

        # print(range, sheetId if sheetId else self.SPREADSHEET_ID, majorDimension)

        values = self.service.spreadsheets().values().get(
            spreadsheetId=sheetId if sheetId else self.SPREADSHEET_ID,
            range=range,
            majorDimension=majorDimension,
        ).execute()
        return values["values"]
    
    def get_all_statuses(self):
        response = self.get_all_values("ROWS", "USER_STATES")
        return response
    
    def get_orgName_by_id(self, telegramId: str):
        values = self.get_all_values("ROWS", "ORGANIZATIONS")

        for row in values:
            if(row[0] == telegramId):
                return row[1]
        
        return None
    
    def get_user_by_id(self, telegramId: str):
        values = self.get_all_values(majorDimension="ROWS", sheet="USERS")

        for row in values:
            if((row[0] == telegramId) or (row[0] == str(telegramId))):
                return row[1]
        
        return None
    
    def add_new_user(self, telegramId: str, name: str):
        self.service.spreadsheets().values().append(
            spreadsheetId=self.SPREADSHEET_ID,
            range=f"'USERS'!1:1000",
            valueInputOption="RAW",
            body={
                'values' : [
                    [telegramId, name],
                ]
            },
        ).execute()

    def calculate_row_by_rowId(self, rowId:str, majorDimension: Literal["ROWS", "COLUMNS"], sheet: Optional[Literal["ORGANIZATIONS", "USERS", "CONFERENCES", "USER_STATES"]]=None, sheetId: Optional[str]=None):
        all_values = self.get_all_values(sheetId=sheetId, majorDimension=majorDimension, sheet=sheet)

        for i in range (len(all_values)):
            if str(rowId) in all_values[i]:
                return i+1
        
        return None
    
    def get_all_org_conference_data(self, telegramId: str) -> list:
        sheetId = self.getSheetId(telegramId)
        allRows = self.get_all_values(sheetId=sheetId, majorDimension="ROWS")
        return allRows

    def get_all_users_data(self):
        all_values = self.get_all_values(majorDimension="ROWS", sheet="USERS")
        return all_values

    def get_all_user_conference(self, userId):
        all_values = self.get_all_values(majorDimension="ROWS", sheet="USERS")
        
        for row in all_values:
            if(str(row[0]) == str(userId)):
                if(len(row) > 2):
                    return ast.literal_eval(row[2])
                else:
                    return []
                
        raise Exception("Конференций не найдено")
    
    def getSheetId(self, telegramId: str):
        rowId = self.calculate_row_by_rowId(telegramId, "ROWS", "ORGANIZATIONS")
        return str((self.get_value(range = f"'ORGANIZATIONS'!C{rowId}", majorDimension="ROWS"))[0][0]).split("/d/")[1]

    def add_confernce(self, telegramId: str, theme:str, time: TimeDict):
        timestamp = int(datetime.timestamp(datetime.now()))
        index = f"{telegramId}_{timestamp}"
        conf_id = self.getSheetId(telegramId)
        
        self.service.spreadsheets().values().append(
            spreadsheetId=conf_id,
            range=f"1:1000",
            valueInputOption='RAW',
            body={
                'values': [
                    [index, theme, str(time), '[]']
                ],
            }
        ).execute()

        return index

    def update_conference(self, telegramId: str, conferenceId: str, theme: str, time: TimeDict):
        
        sheetId = self.getSheetId(telegramId)
        rowId = self.calculate_row_by_rowId(rowId=conferenceId, majorDimension='ROWS', sheetId=sheetId)

        if not rowId:
            raise Exception(f"Конференции {rowId} не существует")
        
        self.service.spreadsheets().values().update(
            spreadsheetId=sheetId,
            range=f"B{rowId}",
            valueInputOption='RAW',
            body={
                'values': [
                    [theme, str(time)]
                ],
            }
        ).execute()

    def add_user_to_conference(self, telegramId: str, conferenceId: str):

        if("_" not in conferenceId):
            raise Exception(f"Конференции {conferenceId} не найдено")

        rowId = self.calculate_row_by_rowId(rowId=conferenceId.split("_")[0], majorDimension="ROWS", sheet="ORGANIZATIONS")
        value = self.get_value(range=f"'ORGANIZATIONS'!C{rowId}", majorDimension="ROWS")

        sheetId = value[0][0]
        
        if(sheetId):
            sheetId = sheetId.split("/d/")[1]
            rowId = self.calculate_row_by_rowId(rowId=conferenceId, sheetId=sheetId, majorDimension="ROWS")

            if(not rowId):
                raise Exception(f"Конференции {conferenceId} не найдено")

            participants: list = ast.literal_eval(self.get_value(sheetId=sheetId, range=f"D{rowId}", majorDimension="ROWS")[0][0])
                        
            if(str(telegramId) in participants or telegramId in participants):
                raise Exception(f"Вы уже учавсвуете в этой конференции")

            participants.append(telegramId)
        
            self.service.spreadsheets().values().update(
                spreadsheetId=sheetId,
                range=f"D{rowId}",
                valueInputOption='RAW',
                body={
                    'values': [
                        [str(participants)]
                    ],
                }
            ).execute()

            lst = self.get_all_user_conference(str(telegramId))
            lst.append(conferenceId)

        else:
            raise Exception(f"Конференции {conferenceId} не найдено")    

    def share_file(self, real_file_id: str, email: str):

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            "creds.json",
            [
                ' https://www.googleapis.com/auth/spreadsheets ',
                ' https://www.googleapis.com/auth/drive ',
            ]
        )

        try:
            service = apiclient.discovery.build("drive", "v3", credentials=credentials)
            ids = []
            file_id = real_file_id

            def callback(request_id, response, exception):
                if exception:
                    print(exception)
                else:
                    print(f"Request_Id: {request_id}")
                    print(f'Permission Id: {response.get("id")}')
                    ids.append(response.get("id"))

            # pylint: disable=maybe-no-member
            batch = service.new_batch_http_request(callback=callback)
            user_permission = {
                "type": "user",
                "role": "writer",
                "emailAddress": email,
            }
            batch.add(
                service.permissions().create(
                    fileId=file_id,
                    body=user_permission,
                    fields="id",
                )
            )

            batch.execute()

        except HttpError as error:
            print(f"An error occurred: {error}")
            ids = None

        return ids

    def createOrganizator(self, telegramId: str, email: str) -> str:
        spreadsheet = {"properties": {"title": f"{telegramId}_CONF"}}
        resp = self.service.spreadsheets().create(body=spreadsheet, fields="spreadsheetId").execute()
        fileId = resp["spreadsheetId"]
        self.share_file(fileId, email)

        self.service.spreadsheets().values().append(
            spreadsheetId=fileId,
            range=f"1:1000",
            valueInputOption="RAW",
            body={
                'values' : [
                    ["CONFERENCE_ID", "THEME", "TIME", "PARTICIPANTS"],
                ]
            },
        ).execute()

        sheet_link = f"https://docs.google.com/spreadsheets/d/{fileId}"

        rowId = self.calculate_row_by_rowId(telegramId, "ROWS")

        self.service.spreadsheets().values().update(
            spreadsheetId=self.SPREADSHEET_ID,
            range=f"'ORGANIZATIONS'!C{rowId}",
            valueInputOption='RAW',
            body={
                'values': [
                    [sheet_link]
                ],
            }
        ).execute()

        return sheet_link