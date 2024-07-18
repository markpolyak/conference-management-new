from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
import uvicorn

from conference_report import *
from conference_program import *
from conference_list import *

app = FastAPI()


@app.get("/conference/{conference_id}/programme")   # endpoint для создания файла с программой конференции
async def root(conference_id: int): # conference_id - id конференции из таблицы с конференциями
    id = get_spreadsheet_id(conference_id)  # получаем id гугл таблицы из файла с конференциями
    if id == "Not found":
        return HTMLResponse(status_code=404)    # если id таблицы не найден, то возвращаем 404
    conference_name = get_conference_name(conference_id)    # по id конференции получаем название
    get_conference_program(id, conference_name)  # создаем отчёт по заданной конференции
    return FileResponse(path="Программа к43.docx", filename="Программа к43.docx")   # возвращаем docx файл с отчётом


@app.get("/conference/{conference_id}/report")   # endpoint для создания файла с отчётом о проведенной конференции
async def root(conference_id: int):
    id = get_spreadsheet_id(conference_id)
    if id == "Not found":
        return HTMLResponse(status_code=404)
    conference_name = get_conference_name(conference_id)
    get_conference_report(id, conference_name)
    return FileResponse(path="Отчёт.docx", filename="Отчёт.docx")


@app.get("/conference/{conference_id}/publications")  # endpoint для создания файла с представляемыми к публикации докладами
async def root(conference_id: int):
    id = get_spreadsheet_id(conference_id)
    if id == "Not found":
        return HTMLResponse(status_code=404)
    get_conference_list(id)
    return FileResponse(path="Список.docx", filename="Список.docx")


if __name__ == '__main__':
    uvicorn.run(app,
                host='localhost',
                port=8000)