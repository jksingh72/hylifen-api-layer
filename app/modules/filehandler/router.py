import logging
import os
import mammoth
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.modules.filehandler.service import process_file_upload, handle_chat_request
from app.core.file_storage import save_upload_file, UPLOAD_DIR

router = APIRouter()
logger = logging.getLogger(__name__)

class FileChatRequest(BaseModel):
    text: str
    session_id: str

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    text: str = Form("I have uploaded a new file.")
):
    try:
        logger.info(f"FileHandler.upload | filename={file.filename} | session={session_id}")
        file_path = await save_upload_file(file)
        logger.info(f"FileHandler.upload | saved_to={file_path}")
        
        response = await process_file_upload(file_path, text, session_id)
        return {"output_text": response}
    except Exception as e:
        logger.error(f"FileHandler.upload FAILED: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_with_files(request: FileChatRequest):
    try:
        response = await handle_chat_request(request.text, request.session_id)
        return {"output_text": response}
    except Exception as e:
        logger.error(f"FileHandler.chat FAILED: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_file(filename: str):
    try:
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(path=file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview/{filename}")
async def preview_file(filename: str):
    try:
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".docx":
            with open(file_path, "rb") as docx_file:
                result = mammoth.convert_to_html(docx_file)
                html = result.value
                styled_html = f"<div style='font-family: sans-serif; padding: 20px;'>{html}</div>"
                return {"html": styled_html}
        return {"html": f"<p>HTML Preview not supported for {ext}</p>"}
    except Exception as e:
        logger.error(f"FileHandler.preview FAILED: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
