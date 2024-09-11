from fastapi import FastAPI, Body, File, UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse
import uvicorn

import json

app = FastAPI()

@app.get("/conferences")
def get_confs(filter: str | None = None):
    if (filter == 'active'):
        confs_file = open("responses/confs_active.json", "r", encoding='utf-8')
    elif (filter == 'past'):
        confs_file = open("responses/confs_past.json", "r", encoding='utf-8')
    elif (filter == 'future'):
        confs_file = open("responses/confs_future.json", "r", encoding='utf-8')
    confs_data = confs_file.read()
    return PlainTextResponse(content=confs_data)

@app.get("/conferences/{id}")
def get_conf_info(id):
    if (id == '1'):
        conf_file = open("responses/conf_1.json", "r", encoding='utf-8')
        conf_data = conf_file.read()
        return PlainTextResponse(content=conf_data)
    elif (id == '2'):
        conf_file = open("responses/conf_2.json", "r", encoding='utf-8')
        conf_data = conf_file.read()
        return PlainTextResponse(content=conf_data)
    elif (id == '3'):
        conf_file = open("responses/conf_3.json", "r", encoding='utf-8')
        conf_data = conf_file.read()
        return PlainTextResponse(content=conf_data)
    else:
        return PlainTextResponse(content={}, status_code=404)
    
@app.post("/conferences/{conference_id}/applications/{application_id}/publication")
def post_publication(conference_id, application_id, body=Body(), file: UploadFile | None = None):
    if (file is not None):
        pub_file = open("responses/conf_1.json", "r", encoding='utf-8')
        pub_data = json.loads(pub_file.read())
        pub_data['publication_title'] = body['publication_title']
        return JSONResponse(content=pub_data)
    else:
        return PlainTextResponse(content={}, status=404)
@app.post("/conferences/{conference_id}/applications")
def post_application(conference_id, body=Body()):
    body['id'] = 999
    print(body)
    return JSONResponse(content=body)

@app.get("/conferences/{conference_id}/applications")
def get_applications(conference_id, telegram_id: str | None = None):
    if (telegram_id is None):
        return PlainTextResponse(content={}, status_code=404)
    app_file = open("responses/application.json", "r", encoding='utf-8')
    app_dict = json.loads(app_file.read())
    app_dict[0]['telegram_id'] = telegram_id
    return JSONResponse(content=app_dict)
