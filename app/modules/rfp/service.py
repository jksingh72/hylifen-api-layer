import logging

from fastapi import UploadFile
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.db.tables import Rfp, RfpChatMessage, RfpDocument, RfpFormatDocument, RfpResponseDocument
from app.modules.rfp.agent import run_stage_turn
from app.modules.rfp.models import (
    ChatResponse,
    DocumentSummary,
    DocumentVersionSummary,
    RfpDetail,
    RfpSummary,
)
from app.modules.rfp.storage import delete_rfp_file, save_rfp_upload

logger = logging.getLogger(__name__)

MAX_DOCUMENTS = 5
DEFAULT_RFP_NAME = "Untitled RFP"

_SESSION_FIELD_BY_STATUS = {
    "SETUP": "setup_session_id",
    "ANALYZING": "analysis_session_id",
    "FORMAT_DRAFT": "format_session_id",
    "RESPONSE_DRAFT": "response_session_id",
}


async def list_rfps(user_id: str) -> list[RfpSummary]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Rfp).where(Rfp.created_by == user_id).order_by(Rfp.created_at.desc())
        )
        rfps = result.scalars().all()
        return [RfpSummary(id=r.id, name=r.name, status=r.status, created_at=r.created_at) for r in rfps]


async def create_rfp(user_id: str, name: str | None) -> RfpSummary:
    async with AsyncSessionLocal() as session:
        if not name:
            # Enforced here (not just client-side) to close the race where the
            # frontend's "reuse the existing Untitled RFP" check runs before its
            # RFP list has finished loading and creates a duplicate.
            existing = await session.execute(
                select(Rfp).where(Rfp.created_by == user_id, Rfp.name == DEFAULT_RFP_NAME)
            )
            reusable = existing.scalars().first()
            if reusable:
                return RfpSummary(
                    id=reusable.id, name=reusable.name, status=reusable.status, created_at=reusable.created_at
                )

        rfp = Rfp(name=name or DEFAULT_RFP_NAME, created_by=user_id, status="SETUP")
        session.add(rfp)
        await session.commit()
        await session.refresh(rfp)
        return RfpSummary(id=rfp.id, name=rfp.name, status=rfp.status, created_at=rfp.created_at)


async def get_rfp_detail(rfp_id: str) -> RfpDetail | None:
    async with AsyncSessionLocal() as session:
        rfp = await session.get(Rfp, rfp_id)
        if not rfp:
            return None

        docs_result = await session.execute(
            select(RfpDocument).where(RfpDocument.rfp_id == rfp_id).order_by(RfpDocument.uploaded_at)
        )
        format_result = await session.execute(
            select(RfpFormatDocument).where(RfpFormatDocument.rfp_id == rfp_id).order_by(RfpFormatDocument.version)
        )
        response_result = await session.execute(
            select(RfpResponseDocument)
            .where(RfpResponseDocument.rfp_id == rfp_id)
            .order_by(RfpResponseDocument.version)
        )

        return RfpDetail(
            id=rfp.id,
            name=rfp.name,
            status=rfp.status,
            created_at=rfp.created_at,
            documents=[
                DocumentSummary(
                    id=d.id,
                    filename=d.filename,
                    uploaded_at=d.uploaded_at,
                    analysis_status=d.analysis_status,
                    analysis_summary=d.analysis_summary,
                )
                for d in docs_result.scalars().all()
            ],
            format_versions=[
                DocumentVersionSummary(id=f.id, version=f.version, is_current=f.is_current, created_at=f.created_at)
                for f in format_result.scalars().all()
            ],
            response_versions=[
                DocumentVersionSummary(id=r.id, version=r.version, is_current=r.is_current, created_at=r.created_at)
                for r in response_result.scalars().all()
            ],
        )


async def upload_document(rfp_id: str, upload_file: UploadFile) -> DocumentSummary:
    async with AsyncSessionLocal() as session:
        rfp = await session.get(Rfp, rfp_id)
        if not rfp:
            raise ValueError("RFP not found")

        count_result = await session.execute(select(RfpDocument).where(RfpDocument.rfp_id == rfp_id))
        existing = count_result.scalars().all()
        if len(existing) >= MAX_DOCUMENTS:
            raise ValueError(f"This RFP already has the maximum of {MAX_DOCUMENTS} documents.")

        storage_path = await save_rfp_upload(rfp_id, upload_file)
        doc = RfpDocument(rfp_id=rfp_id, filename=upload_file.filename, storage_path=storage_path)
        session.add(doc)
        await session.commit()
        await session.refresh(doc)
        analysis_session_id = rfp.analysis_session_id
        doc_id, filename = doc.id, doc.filename

    # Analysis always runs on new uploads, regardless of the RFP's current stage.
    reply, new_session_id = await run_stage_turn(
        "ANALYZING",
        rfp_id,
        f"A new document '{filename}' (document_id={doc_id}) was just uploaded. Please analyze it and save its summary.",
        analysis_session_id,
    )
    logger.info("RFP analysis on upload | rfp_id=%s | doc_id=%s | reply=%s", rfp_id, doc_id, reply)

    async with AsyncSessionLocal() as session:
        rfp = await session.get(Rfp, rfp_id)
        rfp.analysis_session_id = new_session_id
        await session.commit()

        doc = await session.get(RfpDocument, doc_id)
        return DocumentSummary(
            id=doc.id,
            filename=doc.filename,
            uploaded_at=doc.uploaded_at,
            analysis_status=doc.analysis_status,
            analysis_summary=doc.analysis_summary,
        )


async def delete_document(rfp_id: str, document_id: str) -> None:
    async with AsyncSessionLocal() as session:
        doc = await session.get(RfpDocument, document_id)
        if not doc or doc.rfp_id != rfp_id:
            raise ValueError("Document not found")
        delete_rfp_file(doc.storage_path)
        await session.delete(doc)
        await session.commit()


async def get_chat_history(rfp_id: str) -> list[RfpChatMessage]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(RfpChatMessage).where(RfpChatMessage.rfp_id == rfp_id).order_by(RfpChatMessage.created_at)
        )
        return result.scalars().all()


async def get_format_file_path(rfp_id: str, version_id: str) -> str | None:
    async with AsyncSessionLocal() as session:
        doc = await session.get(RfpFormatDocument, version_id)
        if not doc or doc.rfp_id != rfp_id:
            return None
        return doc.storage_path


async def get_response_file_path(rfp_id: str, version_id: str) -> str | None:
    async with AsyncSessionLocal() as session:
        doc = await session.get(RfpResponseDocument, version_id)
        if not doc or doc.rfp_id != rfp_id:
            return None
        return doc.storage_path


async def chat(rfp_id: str, text: str) -> ChatResponse:
    async with AsyncSessionLocal() as session:
        rfp = await session.get(Rfp, rfp_id)
        if not rfp:
            raise ValueError("RFP not found")
        stage = rfp.status
        session_field = _SESSION_FIELD_BY_STATUS.get(stage)
        resume_session_id = getattr(rfp, session_field) if session_field else None

        session.add(RfpChatMessage(rfp_id=rfp_id, stage=stage, role="user", content=text))
        await session.commit()

    reply, new_session_id = await run_stage_turn(stage, rfp_id, text, resume_session_id)

    async with AsyncSessionLocal() as session:
        rfp = await session.get(Rfp, rfp_id)
        if session_field:
            setattr(rfp, session_field, new_session_id)
        session.add(RfpChatMessage(rfp_id=rfp_id, stage=stage, role="assistant", content=reply))
        await session.commit()
        final_status = rfp.status

    return ChatResponse(output_text=reply, status=final_status)
