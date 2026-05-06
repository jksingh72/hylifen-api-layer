import logging
from typing import List, Dict, Callable, Awaitable
from app.modules.fileread.agent import fileread_agent_chain
from app.modules.ocrtext.agent import ocrtext_agent_chain

logger = logging.getLogger(__name__)

# Global session-to-file registry (In-memory for now)
# session_id -> list of file_paths
session_files: Dict[str, List[str]] = {}

def add_file_to_session(session_id: str, file_path: str):
    if session_id not in session_files:
        session_files[session_id] = []
    if file_path not in session_files[session_id]:
        session_files[session_id].append(file_path)

def get_session_files(session_id: str) -> List[str]:
    return session_files.get(session_id, [])

# Registry of specialized agents
FILE_AGENT_REGISTRY: Dict[str, Callable[[List[str], str, str], Awaitable[str]]] = {
    "fileread": fileread_agent_chain,
    "ocrtext": ocrtext_agent_chain
}

async def route_file_request(session_id: str, user_prompt: str, mode: str = "chat") -> str:
    """
    Routes the request to the appropriate file agent based on mode.
    """
    file_paths = get_session_files(session_id)
    if not file_paths:
        return "I don't see any files uploaded for this session. Please upload one first."

    # Determine agent based on mode
    agent_key = "ocrtext" if mode == "ocr" else "fileread"
    target_agent = FILE_AGENT_REGISTRY.get(agent_key, fileread_agent_chain)
    
    logger.info(f"Routing file request | session={session_id} | mode={mode} | files={len(file_paths)}")
    return await target_agent(file_paths, user_prompt, session_id)
