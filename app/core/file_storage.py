import os
import shutil
from fastapi import UploadFile
from pathlib import Path

# Central storage for uploaded files
UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def save_upload_file(upload_file: UploadFile) -> str:
    """
    Saves an uploaded file to the temp_uploads directory and returns the full path.
    """
    try:
        file_path = UPLOAD_DIR / upload_file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return str(file_path.absolute())
    finally:
        await upload_file.close()

def delete_file(file_path: str):
    """
    Deletes a file if it exists.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
