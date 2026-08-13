from app.modules.db_chat.models import DbChatRequest, DbChatResponse
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def process_db_chat(request: DbChatRequest) -> DbChatResponse:
    """
    Orchestrate the DB text-in -> Agent -> text-out pipeline.
    """
    from app.modules.db_chat.agent import db_chat_agent_chain
    
    logger.info(
        "DbChatService.process_db_chat | session_id=%s | text_len=%d",
        request.session_id,
        len(request.text),
    )

    # Hand off to the DB Agent
    output_text = await db_chat_agent_chain(request.text, request.context, request.session_id)

    return DbChatResponse(
        input_text=request.text,
        output_text=output_text,
        model=settings.OPENAI_MODEL,
    )
