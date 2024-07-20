from fastapi import FastAPI, HTTPException
from typing import Optional
from services.applications_google_sheets import get_applications, add_application, update_application, delete_application

from models.request.ApplicationPost import ApplicationPost
from models.request.ApplicationPatch import ApplicationPatch
from models.request.ApplicationDelete import ApplicationDelete

app = FastAPI()


@app.get("/conferences/{conference_id}/applications", response_model_exclude_none=True)
def get_applications_handler(conference_id: str, email: Optional[str] = None, telegram_id: Optional[str] = None, discord_id: Optional[str] = None):
    if sum([bool(email), bool(telegram_id), bool(discord_id)]) != 1:
        raise HTTPException(status_code=400, detail="Должен указан и указан только один параметр")
    try:
        applications = get_applications(conference_id, email=email, telegram_id=telegram_id, discord_id=discord_id)
        if not applications:
            raise HTTPException(status_code=404, detail="Заявки не найдены")
        return applications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conferences/{conference_id}/applications", status_code=201, response_model_exclude_none=True)
def add_application_handler(conference_id: str, application: ApplicationPost):
    try:
        new_application = add_application(conference_id, application)
        return new_application
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/conferences/{conference_id}/applications/{application_id}")
def update_application_handler(conference_id: str, application_id: int, application: ApplicationPatch):
    try:
        updated_application = update_application(conference_id, application_id, application)
        if not updated_application:
            raise HTTPException(status_code=404, detail="Заявка не найдена")
        return updated_application
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/conferences/{conference_id}/applications/{application_id}")
def delete_application_handler(conference_id: str, application_id: int, application: ApplicationDelete):
    if application.telegram_id is None and application.discord_id is None and application.email is None:
        raise HTTPException(status_code=400, detail="Должен быть указать фильтр")
    try:
        print(application.telegram_id, application.discord_id, application.email)
        deleted_application = delete_application(conference_id, application_id, email=application.email, telegram_id=application.telegram_id, discord_id=application.discord_id)
        if not deleted_application:
            raise HTTPException(status_code=404, detail="Заявка не найдена")
        return deleted_application
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))