from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse

import io
import os
from dotenv import load_dotenv
from doc1 import generate_document_programme
from doc2 import generate_document_report
from doc3 import generate_document_publications

app = FastAPI()
security = HTTPBearer()

# Аутентификация и получение данных из Google Sheets
SCOPES = os.getenv("SCOPES")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
CONFERENCES_SPREADSHEET_ID = os.getenv("CONFERENCES_SPREADSHEET_ID")
RANGE_REPORTS = os.getenv("RANGE_REPORTS")
RANGE_COAUTORS = os.getenv("RANGE_COAUTORS")
RANGE_CONFERENCES = os.getenv("RANGE_CONFERENCES")
TOKEN = os.getenv("TOKEN")

# SCOPES='https://www.googleapis.com/auth/spreadsheets.readonly'
# SERVICE_ACCOUNT_FILE = 'connection.json'
# CONFERENCES_SPREADSHEET_ID = '1MRQh6y3QUPrdm43z_R35tOu9ddHDH23liOxZ8xEWLNg'
# RANGE_REPORTS = 'Заявки!A:S'
# RANGE_COAUTORS = 'Авторы!A:J'
# RANGE_CONFERENCES = 'Конференции!A:F'
# TOKEN = 'expected_bearer_token'


scopes_list = SCOPES.split(',')
credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=scopes_list)
service = build('sheets', 'v4', credentials=credentials)

def get_data(range_cells, spreadsheet_id):
    print(range_cells)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_cells).execute()
    values = result.get('values', [])
   
    if not values:
        print('No data found.')
    else:
        columns = values[0]
        print(columns)
        
        # Приведение всех строк данных к одной длине с заполнением пустых значений
        max_columns = len(columns)
        for row in values[1:]:
            while len(row) < max_columns:
                row.append('')
        
        data = pd.DataFrame(values[1:], columns=columns)
        
        # Заполняем отсутствующие значения пустыми строками
        data = data.fillna('')

        return data
    
def verify_token(token: str):
    if token == TOKEN:
        return True
    return False

def reports_coautors_fusion(reports, collaborators):
    # Добавляем столбец для соавторов
    reports['coauthors'] = reports.apply(lambda x: [], axis=1)
    for index_report, report in reports.iterrows():
        id = report['id']
        for index_coll, collaborator in collaborators.iterrows():
            if collaborator['id'] == id:
                reports.at[index_report, 'coauthors'].append({
                    'surname': collaborator['surname'],
                    'name': collaborator['name'],
                    'patronymic': collaborator['patronymic']
                })
    return reports

def generate_document(conference_id: int, generate_func, filename: str, authorization: str):
    token = authorization.split("Bearer ")[-1] if authorization else ''
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    conferences = get_data(RANGE_CONFERENCES, CONFERENCES_SPREADSHEET_ID)
    for index, row in conferences.iterrows():
        if str(conference_id) == row['conference_id']:
            if row['spreadsheet_id'] == '':
                raise HTTPException(status_code=404, detail="spreadsheet_id is empty")
            short_name = row['name_rus_short'] if row['name_rus_short'] is not None else ''

            reports = get_data(RANGE_REPORTS, row['spreadsheet_id'])
            collaborators = get_data(RANGE_COAUTORS, row['spreadsheet_id'])
            reports = reports_coautors_fusion(reports, collaborators)
            doc = generate_func(reports, short_name)
            file_stream = io.BytesIO()
            doc.save(file_stream)
            file_stream.seek(0)
            return StreamingResponse(
                file_stream,
                media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
    raise HTTPException(status_code=404, detail="Conference not found")

@app.get('/conferences/{conference_id}/programme')
def generate_programme(conference_id: int, token: HTTPAuthorizationCredentials = Depends(security)):
    token = token.credentials
    return generate_document(conference_id, generate_document_programme, "programme.docx", token)

@app.get('/conferences/{conference_id}/report')
def generate_report(conference_id: int, token: HTTPAuthorizationCredentials = Depends(security)):
    token = token.credentials
    return generate_document(conference_id, generate_document_report, "report.docx", token)

@app.get('/conferences/{conference_id}/publications')
def generate_publications(conference_id: int, token: HTTPAuthorizationCredentials = Depends(security)):
    token = token.credentials
    return generate_document(conference_id, generate_document_publications, "publications.docx", token)