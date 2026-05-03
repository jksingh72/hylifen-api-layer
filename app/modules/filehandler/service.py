import logging
from app.modules.filehandler.orchestrator import route_file_request, add_file_to_session

logger = logging.getLogger(__name__)

async def process_file_upload(file_path: str, user_prompt: str, session_id: str) -> str:
    """
    Called when a NEW file is uploaded. Registers the file and then starts/continues the chat.
    """
    logger.info("FileHandlerService.process_file_upload | session_id=%s | file_path=%s", session_id, file_path)
    add_file_to_session(session_id, file_path)
    return await route_file_request(session_id, user_prompt)

async def handle_chat_request(user_prompt: str, session_id: str) -> str:
    """
    Called for follow-up chat messages that don't include a new file upload.
    """
    logger.info("FileHandlerService.handle_chat_request | session_id=%s", session_id)
    return await route_file_request(session_id, user_prompt)
