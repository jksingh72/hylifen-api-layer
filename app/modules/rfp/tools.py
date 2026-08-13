"""
Claude Agent SDK tool definitions for the RFP/RFI module.
Each get_*_tools(rfp_id) factory returns the tool set for one of the four stage
agents, scoped to a single RFP so the agent can't act outside its own record.
"""
from claude_agent_sdk import tool

from app.core.database import AsyncSessionLocal
from app.db.tables import Rfp, RfpDocument, RfpFormatDocument, RfpResponseDocument
from app.modules.rfp.storage import (
    extract_text_from_file,
    generate_format_docx,
    generate_response_docx,
    read_format_sections,
)
from sqlalchemy import select, func


def _text_result(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}


def get_setup_tools(rfp_id: str) -> list:
    @tool(
        "read_document_text",
        "Reads the extracted text content of an uploaded source document by its document_id.",
        {"document_id": str},
    )
    async def read_document_text(args):
        async with AsyncSessionLocal() as session:
            doc = await session.get(RfpDocument, args["document_id"])
            if not doc or doc.rfp_id != rfp_id:
                return _text_result("Document not found.")
            return _text_result(extract_text_from_file(doc.storage_path))

    @tool(
        "list_documents",
        "Lists all source documents currently uploaded to this RFP.",
        {},
    )
    async def list_documents(args):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(RfpDocument).where(RfpDocument.rfp_id == rfp_id))
            docs = result.scalars().all()
            if not docs:
                return _text_result("No documents uploaded yet.")
            lines = [f"- {d.id}: {d.filename}" for d in docs]
            return _text_result("\n".join(lines))

    @tool(
        "set_rfp_name",
        "Sets (or updates) the name of this RFP, e.g. after suggesting one from the main document.",
        {"name": str},
    )
    async def set_rfp_name(args):
        async with AsyncSessionLocal() as session:
            rfp = await session.get(Rfp, rfp_id)
            rfp.name = args["name"]
            await session.commit()
            return _text_result(f"RFP name set to '{args['name']}'.")

    @tool(
        "mark_setup_complete",
        "Call this once the user confirms the RFP name and setup is done, to move on to document analysis.",
        {},
    )
    async def mark_setup_complete(args):
        async with AsyncSessionLocal() as session:
            rfp = await session.get(Rfp, rfp_id)
            rfp.status = "ANALYZING"
            await session.commit()
            return _text_result("Setup complete. Moving to document analysis.")

    return [read_document_text, list_documents, set_rfp_name, mark_setup_complete]


def get_analysis_tools(rfp_id: str) -> list:
    @tool(
        "read_document_text",
        "Reads the extracted text content of an uploaded source document by its document_id.",
        {"document_id": str},
    )
    async def read_document_text(args):
        async with AsyncSessionLocal() as session:
            doc = await session.get(RfpDocument, args["document_id"])
            if not doc or doc.rfp_id != rfp_id:
                return _text_result("Document not found.")
            return _text_result(extract_text_from_file(doc.storage_path))

    @tool(
        "list_documents",
        "Lists all source documents for this RFP along with their analysis status and, if analyzed, their summary.",
        {},
    )
    async def list_documents(args):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(RfpDocument).where(RfpDocument.rfp_id == rfp_id))
            docs = result.scalars().all()
            if not docs:
                return _text_result("No documents uploaded yet.")
            lines = []
            for d in docs:
                summary = f" | summary: {d.analysis_summary}" if d.analysis_summary else ""
                lines.append(f"- {d.id}: {d.filename} [{d.analysis_status}]{summary}")
            return _text_result("\n".join(lines))

    @tool(
        "save_document_summary",
        "Saves the analysis summary for a document, marking it as analyzed.",
        {"document_id": str, "summary": str},
    )
    async def save_document_summary(args):
        async with AsyncSessionLocal() as session:
            doc = await session.get(RfpDocument, args["document_id"])
            if not doc or doc.rfp_id != rfp_id:
                return _text_result("Document not found.")
            doc.analysis_summary = args["summary"]
            doc.analysis_status = "done"
            await session.commit()
            return _text_result(f"Summary saved for {doc.filename}.")

    @tool(
        "mark_analysis_complete",
        "Call this once the user asks to build the response document format, to move to the format stage.",
        {},
    )
    async def mark_analysis_complete(args):
        async with AsyncSessionLocal() as session:
            rfp = await session.get(Rfp, rfp_id)
            rfp.status = "FORMAT_DRAFT"
            await session.commit()
            return _text_result("Moving to response format creation.")

    return [read_document_text, list_documents, save_document_summary, mark_analysis_complete]


def get_format_tools(rfp_id: str) -> list:
    @tool(
        "list_analysis_summaries",
        "Lists every analyzed document's summary for this RFP, used as the basis for the response format.",
        {},
    )
    async def list_analysis_summaries(args):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(RfpDocument).where(RfpDocument.rfp_id == rfp_id))
            docs = result.scalars().all()
            analyzed = [d for d in docs if d.analysis_summary]
            if not analyzed:
                return _text_result("No analyzed documents yet.")
            lines = [f"- {d.filename}: {d.analysis_summary}" for d in analyzed]
            return _text_result("\n".join(lines))

    @tool(
        "generate_format",
        "Generates a new version of the response document FORMAT (.docx) containing only the given section titles, in order.",
        {"section_titles": list[str]},
    )
    async def generate_format(args):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(func.max(RfpFormatDocument.version)).where(RfpFormatDocument.rfp_id == rfp_id)
            )
            next_version = (result.scalar() or 0) + 1
            path = generate_format_docx(rfp_id, next_version, args["section_titles"])

            await session.execute(
                RfpFormatDocument.__table__.update()
                .where(RfpFormatDocument.rfp_id == rfp_id)
                .values(is_current=False)
            )
            session.add(
                RfpFormatDocument(rfp_id=rfp_id, version=next_version, storage_path=path, is_current=True)
            )
            await session.commit()
            return _text_result(f"Generated format version {next_version} with sections: {', '.join(args['section_titles'])}.")

    @tool(
        "mark_format_complete",
        "Call this once the user approves the format, to move on to writing the actual response content.",
        {},
    )
    async def mark_format_complete(args):
        async with AsyncSessionLocal() as session:
            rfp = await session.get(Rfp, rfp_id)
            rfp.status = "RESPONSE_DRAFT"
            await session.commit()
            return _text_result("Format approved. Moving to response writing.")

    return [list_analysis_summaries, generate_format, mark_format_complete]


def get_response_tools(rfp_id: str) -> list:
    @tool(
        "get_current_format",
        "Gets the section titles from the current response format document.",
        {},
    )
    async def get_current_format(args):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(RfpFormatDocument)
                .where(RfpFormatDocument.rfp_id == rfp_id, RfpFormatDocument.is_current == True)  # noqa: E712
            )
            fmt = result.scalars().first()
            if not fmt:
                return _text_result("No format document exists yet.")
            titles = read_format_sections(fmt.storage_path)
            return _text_result("Sections: " + ", ".join(titles))

    @tool(
        "list_analysis_summaries",
        "Lists every analyzed document's summary for this RFP, to draw on when writing response content.",
        {},
    )
    async def list_analysis_summaries(args):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(RfpDocument).where(RfpDocument.rfp_id == rfp_id))
            docs = result.scalars().all()
            analyzed = [d for d in docs if d.analysis_summary]
            if not analyzed:
                return _text_result("No analyzed documents yet.")
            lines = [f"- {d.filename}: {d.analysis_summary}" for d in analyzed]
            return _text_result("\n".join(lines))

    @tool(
        "save_response",
        "Generates a new version of the response document (.docx) with the given section-title to content mapping.",
        {"sections": dict},
    )
    async def save_response(args):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(func.max(RfpResponseDocument.version)).where(RfpResponseDocument.rfp_id == rfp_id)
            )
            next_version = (result.scalar() or 0) + 1
            path = generate_response_docx(rfp_id, next_version, args["sections"])

            await session.execute(
                RfpResponseDocument.__table__.update()
                .where(RfpResponseDocument.rfp_id == rfp_id)
                .values(is_current=False)
            )
            session.add(
                RfpResponseDocument(rfp_id=rfp_id, version=next_version, storage_path=path, is_current=True)
            )
            await session.commit()
            return _text_result(f"Generated response version {next_version}.")

    @tool(
        "mark_response_complete",
        "Call this once the user confirms the response document is finished.",
        {},
    )
    async def mark_response_complete(args):
        async with AsyncSessionLocal() as session:
            rfp = await session.get(Rfp, rfp_id)
            rfp.status = "COMPLETE"
            await session.commit()
            return _text_result("RFP response marked complete.")

    return [get_current_format, list_analysis_summaries, save_response, mark_response_complete]
