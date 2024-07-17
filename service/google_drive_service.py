from tempfile import NamedTemporaryFile
from fastapi import UploadFile, HTTPException
from pydrive.drive import GoogleDrive

def get_or_create_folder(drive: GoogleDrive, folder_name: str, parent_folder_id: str=None):
    query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"

    file_list = drive.ListFile({'q': query}).GetList()

    if file_list:
        return file_list[0]
    else:
        folder_metadata = {
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [{'id': parent_folder_id}] if parent_folder_id else []
        }
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        return folder

async def upload_file(drive: GoogleDrive, file: UploadFile, folder_id: str):
    if file.filename == "":
        raise HTTPException(400, "File to upload has not been selected")

    if file.content_type not in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(400, "Invalid file type. Only PDF files are allowed")

    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file.file.read())
        temp_file_path = temp_file.name

    #folder = get_or_create_folder(drive, folder_name)

    file_drive = drive.CreateFile({'title': file.filename, 'parents': [{'id': folder_id}]})
    file_drive.SetContentFile(temp_file_path)
    file_drive.Upload()

    return f'https://drive.google.com/uc?id={file_drive["id"]}'