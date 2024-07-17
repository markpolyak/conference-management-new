import os
import json
from google.oauth2 import service_account
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')

#CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), 'client_secret.json')

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

def create_jwt_token(credentials):
    request = Request()
    credentials.refresh(request)
    return credentials.token

def save_token(token, token_file):
    with open(token_file, 'w') as f:
        json.dump({"token": token}, f)

def load_token(token_file):
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            return json.load(f).get("token")
    return None

"""
def get_oauth_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE, scopes=SCOPES)
    creds = flow.run_local_server(port=8888)
    return creds.token
"""

VALID_TOKEN = load_token(TOKEN_FILE)

if not VALID_TOKEN:
    VALID_TOKEN = create_jwt_token(credentials)
    save_token(VALID_TOKEN, TOKEN_FILE)

#OAUTH_TOKEN = get_oauth_credentials()

#print(f"VALID_TOKEN: {VALID_TOKEN}")
#print(f"OAUTH_TOKEN: {OAUTH_TOKEN}")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SENDER_EMAIL = SMTP_USER

