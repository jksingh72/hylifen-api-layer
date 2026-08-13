from pydantic import BaseModel, Field
from datetime import datetime

class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="The title of the note.")
    content: str = Field(..., description="The content of the note.")

class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255, description="The updated title.")
    content: str | None = Field(default=None, description="The updated content.")

class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
