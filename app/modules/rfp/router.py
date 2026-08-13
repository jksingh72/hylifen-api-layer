import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.core.security import AuthenticatedUser, get_current_user
from app.modules.rfp import service
from app.modules.rfp.models import (
    ChatRequest,
    ChatResponse,
    CreateRfpRequest,
    DocumentSummary,
    RfpDetail,
    RfpSummary,
)

router = APIRouter()


@router.get("/", response_model=list[RfpSummary])
async def list_rfps(current_user: AuthenticatedUser = Depends(get_current_user)):
    return await service.list_rfps(current_user.user_id)


@router.post("/", response_model=RfpSummary)
async def create_rfp(
    request: CreateRfpRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return await service.create_rfp(current_user.user_id, request.name)


@router.get("/{rfp_id}", response_model=RfpDetail)
async def get_rfp(rfp_id: str, current_user: AuthenticatedUser = Depends(get_current_user)):
    detail = await service.get_rfp_detail(rfp_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFP not found")
    return detail


@router.post("/{rfp_id}/documents", response_model=DocumentSummary)
async def upload_document(
    rfp_id: str,
    file: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        return await service.upload_document(rfp_id, file)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{rfp_id}/documents/{document_id}")
async def delete_document(
    rfp_id: str,
    document_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        await service.delete_document(rfp_id, document_id)
        return {"deleted": True}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{rfp_id}/chat/history")
async def chat_history(rfp_id: str, current_user: AuthenticatedUser = Depends(get_current_user)):
    messages = await service.get_chat_history(rfp_id)
    return [
        {"role": m.role, "content": m.content, "stage": m.stage, "created_at": m.created_at} for m in messages
    ]


@router.post("/{rfp_id}/chat", response_model=ChatResponse)
async def chat(
    rfp_id: str,
    request: ChatRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        return await service.chat(rfp_id, request.text)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"RFP agent call failed: {exc}") from exc


@router.get("/{rfp_id}/download/format/{version_id}")
async def download_format(
    rfp_id: str, version_id: str, current_user: AuthenticatedUser = Depends(get_current_user)
):
    path = await service.get_format_file_path(rfp_id, version_id)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Format document not found")
    return FileResponse(path=path, filename=os.path.basename(path))


@router.get("/{rfp_id}/download/response/{version_id}")
async def download_response(
    rfp_id: str, version_id: str, current_user: AuthenticatedUser = Depends(get_current_user)
):
    path = await service.get_response_file_path(rfp_id, version_id)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Response document not found")
    return FileResponse(path=path, filename=os.path.basename(path))
