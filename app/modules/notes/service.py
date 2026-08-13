from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.tables import Note
from app.modules.notes.models import NoteCreate, NoteUpdate

async def list_notes(user_id: str, db: AsyncSession) -> list[Note]:
    """Retrieve all notes belonging to the specified user, ordered by last update."""
    result = await db.execute(
        select(Note).where(Note.user_id == user_id).order_by(Note.updated_at.desc())
    )
    return list(result.scalars().all())

async def create_note(user_id: str, payload: NoteCreate, db: AsyncSession) -> Note:
    """Create a new note for the specified user."""
    note = Note(
        title=payload.title,
        content=payload.content,
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(note)
    await db.flush()
    return note

async def update_note(user_id: str, note_id: str, payload: NoteUpdate, db: AsyncSession) -> Note:
    """Update an existing note if it belongs to the user."""
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    )
    note = result.scalars().first()
    if not note:
        raise ValueError("Note not found or access denied")
    
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    
    note.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return note

async def delete_note(user_id: str, note_id: str, db: AsyncSession) -> None:
    """Delete a note if it belongs to the user."""
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    )
    note = result.scalars().first()
    if not note:
        raise ValueError("Note not found or access denied")
    
    await db.delete(note)
    await db.flush()
