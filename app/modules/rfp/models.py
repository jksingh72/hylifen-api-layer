from datetime import datetime

from pydantic import BaseModel


class RfpSummary(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime


class DocumentSummary(BaseModel):
    id: str
    filename: str
    uploaded_at: datetime
    analysis_status: str
    analysis_summary: str | None = None


class DocumentVersionSummary(BaseModel):
    id: str
    version: int
    is_current: bool
    created_at: datetime


class RfpDetail(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime
    documents: list[DocumentSummary]
    format_versions: list[DocumentVersionSummary]
    response_versions: list[DocumentVersionSummary]


class CreateRfpRequest(BaseModel):
    name: str | None = None


class ChatMessage(BaseModel):
    role: str
    content: str
    created_at: datetime


class ChatRequest(BaseModel):
    text: str


class ChatResponse(BaseModel):
    output_text: str
    status: str
