from fastapi import FastAPI, HTTPException, Path, Body, Header
from typing import List, Optional
from .crud import get_conference_responses, add_application, get_conference_by_id, \
    update_application, delete_application, get_user_applications
from .schemas import ConferenceResponse, ApplicationResponse
from .models import Application, Conference, DeleteData
from .config import VALID_TOKEN


app = FastAPI()

@app.get("/conferences", response_model=List[ConferenceResponse])
def read_conferences(filter: str = 'all'):
    try:
        response = get_conference_responses(filter)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/conferences/{conference_id}", response_model=Conference)
def read_conference(conference_id: int, authorization: Optional[str] = Header(None)):
    try:
        response = get_conference_by_id(conference_id)
        if not response:
            raise HTTPException(status_code=404, detail="Conference not found")

        if authorization and authorization.startswith("Bearer "):
            token = authorization.split("Bearer ")[1]
            # print(f"Received token: {token}")
            # print(f"Expected token: {VALID_TOKEN}")
            if token == VALID_TOKEN:
                response.google_spreadsheet = response.sheet_id
            else:
                raise HTTPException(status_code=403, detail="Invalid token")

        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/conferences/{conference_id}/applications", response_model=ApplicationResponse)
def create_application(conference_id: int = Path(...), application: Application = Body(...)):
    try:
        response = add_application(conference_id, application)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.patch("/conferences/{conference_id}/applications/{application_id}", response_model=ApplicationResponse)
def patch_application(conference_id: int, application_id: int, update_data: dict = Body(...)):
    try:
        response = update_application(conference_id, application_id, update_data)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/conferences/{conference_id}/applications/{application_id}")
def remove_application(conference_id: int, application_id: int, delete_data: DeleteData = Body(...)):
    try:
        response = delete_application(conference_id, application_id, delete_data.dict(exclude_none=True))
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))



@app.get("/applications/{telegram_id}", response_model=List[ApplicationResponse])
def read_applications(telegram_id: str):
    try:
        response = get_user_applications(telegram_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

