import asyncio
import os
import sys
from typing import Any, Dict
from aiogram import Bot
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from sheetsController import SheetsController
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import cfg
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

sheetsController = SheetsController(cfg.SPREADSHEET_ID)

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.get("/getOrgName")
def getOrgName(telegramId: str = Query(..., description="Telegram ID of the user")):
    org_name = sheetsController.get_orgName_by_id(telegramId)

    if(org_name):
        return JSONResponse(content={"org_name": org_name}, status_code=200)
    else:
        return JSONResponse(content={"org_name": org_name}, status_code=404)

@app.get("/getUserName")
def getUserName(telegramId: str = Query(..., description="Telegram ID of the user")):
    user_name = sheetsController.get_user_by_id(telegramId)

    if(user_name):
        return JSONResponse(content={"user_name": user_name}, status_code=200)
    else:
        return JSONResponse(content={"user_name": user_name}, status_code=404)
    
@app.get("/getAllOrgConferenceWithData")
def getAllOrgConferenceWithData(telegramId: str = Query(..., description="Telegram ID of the user")):
    try:
        response = sheetsController.get_all_org_conference_data(telegramId)
        return JSONResponse(content={"response": response}, status_code=200)
    except Exception as e:
        raise e
    
@app.get("/getAllConferenceData")
def getAllConference(telegramId: str = Query()):
    try:

        rowId = sheetsController.calculate_row_by_rowId(telegramId, majorDimension="ROWS", sheet="ORGANIZATIONS")
        value = sheetsController.get_value(range=f"'ORGANIZATIONS'!C{rowId}", majorDimension="ROWS")
        sheetId = value[0][0].split("/d/")[1]
        
        rawData = sheetsController.get_all_values(majorDimension="ROWS", sheetId=sheetId)
        return JSONResponse(content={"response": rawData}, status_code=200)
    
    except Exception as e:
        raise e
    
@app.get("/getSheetId")
def getSheetId(telegramId: str = Query(..., description="Telegram ID of the user")):
    try:
        rowId = sheetsController.calculate_row_by_rowId(telegramId, "ROWS", "ORGANIZATIONS")
        value = sheetsController.get_value(sheetId=None, range=f"'ORGANIZATIONS'!C{rowId}", majorDimension="ROWS")

        if(value[0][0]):
            return JSONResponse(content={"message": value[0][0]}, status_code=200)
        else:
            return JSONResponse(content={"message": False}, status_code=200)

    except Exception as e:
        raise e
    
@app.get("/getApplicationDocx")
def getApplicationDocx():
    try:
        file_path = "./files/application.docx"
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename="application.docx")
        else:
            raise HTTPException(status_code=404, detail="File not found")

    except Exception as e:
        raise e
    
@app.get("/getConferenceReportDocx")
def getConferenceReportDocx():
    try:
        file_path = "./files/report.docx"
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename="application.docx")
        else:
            raise HTTPException(status_code=404, detail="File not found")

    except Exception as e:
        raise e
    
@app.get("/getSubbmittedRepostsDocx")
def getSubbmittedRepostsDocx():
    try:
        file_path = "./files/submittedReposts.docx"
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename="application.docx")
        else:
            raise HTTPException(status_code=404, detail="File not found")

    except Exception as e:
        raise e

# POST
@app.post("/addUser")
def getUserName(body: Dict[Any, Any]):
    telegramId = body["telegramId"]
    name = body["name"]
    # chatId = body["chatId"]

    sheetsController.add_new_user(telegramId, name)

@app.post("/addConference")
def addConference(body: Dict[Any, Any]):
    telegramId = body["telegramId"]
    theme = body["theme"]
    time = body["time"]

    try:
        index = sheetsController.add_confernce(str(telegramId), theme, time)
        return JSONResponse(content={"message": str(index)}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

@app.post("/updateConference")
def addConference(body: Dict[Any, Any]):
    try:
        sheetsController.update_conference(body["telegramId"], body["conferenceId"], body["theme"], body["time"])
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
    
@app.post("/addUserToConference")
def addUserToConference(body: Dict[Any, Any]):
    try:
        sheetsController.add_user_to_conference(body["telegramId"], body["conferenceId"])
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

@app.post("/createOrganizator")
def createOrganizator(body: Dict[Any, Any]):
    try:
        sheet_id = sheetsController.createOrganizator(body["telegramId"], body["email"])
        return JSONResponse(content={"message": str(sheet_id)}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

userBot = Bot(token=cfg.USER_BOT, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

@app.post("/sendAlerts")
async def createOrganizator(body: Dict[Any, Any]):
    try:
        message: str = body["message"]
        userId: list = body["userId"]
        
        await userBot.send_message(userId, message, parse_mode=ParseMode.HTML)
        return JSONResponse(content={"message": "true"}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

if __name__ == '__main__':
    uvicorn.run(app, host=cfg.SERVER_HOST, port=cfg.SERVER_PORT)
