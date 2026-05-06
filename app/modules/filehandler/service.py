import logging
from app.modules.filehandler.orchestrator import route_file_request, add_file_to_session

logger = logging.getLogger(__name__)

async def process_file_upload(file_path: str, user_prompt: str, session_id: str, mode: str = "chat") -> str:
    """
    Handles a new file upload: registers it to the session and triggers initial analysis.
    """
    logger.info("FileHandlerService.process_file_upload | session_id=%s | file_path=%s", session_id, file_path)
    add_file_to_session(session_id, file_path)
    return await route_file_request(session_id, user_prompt, mode=mode)

async def handle_chat_request(user_prompt: str, session_id: str, mode: str = "chat") -> str:
    """
    Handles a follow-up chat request about the files in a session.
    """
    logger.info("FileHandlerService.handle_chat_request | session_id=%s", session_id)
    return await route_file_request(session_id, user_prompt, mode=mode)
