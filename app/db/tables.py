import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ExampleRecord(Base):
    """
    Example ORM table — copy this pattern for each new module.
    Run `uv run alembic revision --autogenerate -m "add example_records"` after adding a table.
    """
    __tablename__ = "example_records"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Rfp(Base):
    """An RFP/RFI being analyzed. Status drives which agent handles the current chat turn."""
    __tablename__ = "rfp"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="SETUP")
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    # Claude Agent SDK session ids, one per stage, so each agent's conversation
    # can be resumed across turns instead of starting fresh every message.
    setup_session_id: Mapped[str | None] = mapped_column(String, nullable=True)
    analysis_session_id: Mapped[str | None] = mapped_column(String, nullable=True)
    format_session_id: Mapped[str | None] = mapped_column(String, nullable=True)
    response_session_id: Mapped[str | None] = mapped_column(String, nullable=True)


class RfpDocument(Base):
    """A source document uploaded to an RFP (max 5 enforced at the API layer)."""
    __tablename__ = "rfp_document"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    rfp_id: Mapped[str] = mapped_column(String, ForeignKey("rfp.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    analysis_status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    analysis_summary: Mapped[str | None] = mapped_column(Text, nullable=True)


class RfpFormatDocument(Base):
    """A version of the generated response-document format (.docx). New versions never overwrite old rows."""
    __tablename__ = "rfp_format_document"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    rfp_id: Mapped[str] = mapped_column(String, ForeignKey("rfp.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class RfpResponseDocument(Base):
    """A version of the generated response document (.docx), filled in section by section."""
    __tablename__ = "rfp_response_document"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    rfp_id: Mapped[str] = mapped_column(String, ForeignKey("rfp.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class RfpChatMessage(Base):
    """Persisted chat history per RFP/stage, backing the scrollable chat window."""
    __tablename__ = "rfp_chat_message"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    rfp_id: Mapped[str] = mapped_column(String, ForeignKey("rfp.id"), nullable=False)
    stage: Mapped[str] = mapped_column(String(32), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Note(Base):
    """Persisted notes database table, backing the Notes panel in the Book Reader module."""
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

