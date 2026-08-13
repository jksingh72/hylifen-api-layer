from pydantic import BaseModel, Field
from typing import Optional

class DbChatRequest(BaseModel):
    text: str = Field(..., max_length=4000)
    context: Optional[str] = None
    session_id: str = "default_session"

class DbChatResponse(BaseModel):
    input_text: str
    output_text: str
    model: str
