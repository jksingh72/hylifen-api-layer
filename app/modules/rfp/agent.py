"""
RFP/RFI Agents
--------------
Four Claude Agent SDK agents, one per RFP stage (SETUP, ANALYZING, FORMAT_DRAFT,
RESPONSE_DRAFT). Each stage owns its own system prompt and tool set (app.modules.rfp.tools)
and resumes its own Claude session (Rfp.<stage>_session_id) so conversation context
persists across turns without re-sending the whole history every time.
"""
import logging

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
    query,
)

from app.core.config import settings
from app.modules.rfp.tools import (
    get_analysis_tools,
    get_format_tools,
    get_response_tools,
    get_setup_tools,
)

logger = logging.getLogger(__name__)

SETUP_PROMPT = (
    "You are the Setup agent for an RFP/RFI response tool. Your job: help the user name this RFP. "
    "If a main document has been uploaded, use 'read_document_text' to inspect it, extract key "
    "identifying information (title, issuing organization, subject), and suggest a concise RFP name. "
    "Use 'set_rfp_name' once the user confirms a name (or supplies their own). "
    "Once the name is set and the user is ready to proceed, call 'mark_setup_complete'. "
    "Keep replies short and conversational."
)

ANALYSIS_PROMPT = (
    "You are the Analysis agent for an RFP/RFI response tool. Whenever asked to analyze a document, use "
    "'read_document_text' to read it, then write a concise summary of its key requirements/content and save it "
    "with 'save_document_summary'. Use 'list_documents' to see what's uploaded and their status. "
    "Answer the user's questions about the uploaded documents using the summaries and, if needed, "
    "'read_document_text' for more detail. When the user asks you to create the response format, "
    "call 'mark_analysis_complete'. Keep replies concise."
)

FORMAT_PROMPT = (
    "You are the Document-Format agent for an RFP/RFI response tool. Use 'list_analysis_summaries' to see what "
    "the RFP requires, then propose a list of response section titles and call 'generate_format' to create the "
    "format document. Discuss changes with the user and regenerate with 'generate_format' as needed — each call "
    "creates a new version, prior versions are preserved. Once the user approves the format, call "
    "'mark_format_complete'. Keep replies concise."
)

RESPONSE_PROMPT = (
    "You are the Response-Creator agent for an RFP/RFI response tool. Use 'get_current_format' to see the "
    "approved section titles and 'list_analysis_summaries' for source material, then write section content and "
    "call 'save_response' with a mapping of section title to written content for ALL sections. Each call to "
    "'save_response' creates a new version; prior versions are preserved. Take the user's edits/instructions and "
    "regenerate with 'save_response' as needed. Once the user confirms it's finished, call "
    "'mark_response_complete'. Keep replies concise."
)

_STAGE_CONFIG = {
    "SETUP": (SETUP_PROMPT, get_setup_tools),
    "ANALYZING": (ANALYSIS_PROMPT, get_analysis_tools),
    "FORMAT_DRAFT": (FORMAT_PROMPT, get_format_tools),
    "RESPONSE_DRAFT": (RESPONSE_PROMPT, get_response_tools),
}


async def run_stage_turn(
    stage: str, rfp_id: str, text: str, resume_session_id: str | None
) -> tuple[str, str | None]:
    """Runs one chat turn against the agent for the given stage. Returns (reply_text, new_session_id)."""
    if stage not in _STAGE_CONFIG:
        return (f"This RFP is in status '{stage}' and cannot currently take chat input.", resume_session_id)

    system_prompt, tools_factory = _STAGE_CONFIG[stage]
    tools = tools_factory(rfp_id)
    server = create_sdk_mcp_server(name="rfp_tools", tools=tools)
    allowed_tools = [f"mcp__rfp_tools__{t.name}" for t in tools]

    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        mcp_servers={"rfp_tools": server},
        allowed_tools=allowed_tools,
        permission_mode="bypassPermissions",
        resume=resume_session_id,
        env={"ANTHROPIC_API_KEY": settings.ANTHROPIC_API_KEY},
    )

    reply_parts: list[str] = []
    new_session_id = resume_session_id
    try:
        async for message in query(prompt=text, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        reply_parts.append(block.text)
            elif isinstance(message, ResultMessage):
                new_session_id = message.session_id
                if message.result:
                    reply_parts = [message.result]
    except Exception as exc:
        logger.error("RFP agent turn failed | stage=%s | rfp_id=%s | %s", stage, rfp_id, exc, exc_info=True)
        return (f"I encountered an error processing that: {exc}", resume_session_id)

    return ("".join(reply_parts).strip() or "(no response)", new_session_id)
