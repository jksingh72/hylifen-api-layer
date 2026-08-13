from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import AuthenticatedUser, get_current_user
from app.modules.notes.models import NoteCreate, NoteUpdate, NoteResponse
from app.modules.notes import service as notes_service

router = APIRouter()

@router.get("", response_model=list[NoteResponse], summary="List all user notes")
async def list_notes(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await notes_service.list_notes(user_id=current_user.user_id, db=db)

@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED, summary="Create a new note")
async def create_note(
    payload: NoteCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await notes_service.create_note(user_id=current_user.user_id, payload=payload, db=db)

@router.put("/{note_id}", response_model=NoteResponse, summary="Update an existing note")
async def update_note(
    note_id: str,
    payload: NoteUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await notes_service.update_note(user_id=current_user.user_id, note_id=note_id, payload=payload, db=db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a note")
async def delete_note(
    note_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        await notes_service.delete_note(user_id=current_user.user_id, note_id=note_id, db=db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
