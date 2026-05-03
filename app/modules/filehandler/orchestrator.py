import logging
from typing import Callable, Dict, Awaitable, List
from app.modules.fileread.agent import fileread_agent_chain

logger = logging.getLogger(__name__)

# Registry mapping session_id -> List of file_paths
session_files: Dict[str, List[str]] = {}

def add_file_to_session(session_id: str, file_path: str):
    if session_id not in session_files:
        session_files[session_id] = []
    if file_path not in session_files[session_id]:
        session_files[session_id].append(file_path)

def get_session_files(session_id: str) -> List[str]:
    return session_files.get(session_id, [])

# Registry of file-specialized agents
FILE_AGENT_REGISTRY: Dict[str, Callable[[List[str], str, str], Awaitable[str]]] = {
    "fileread": fileread_agent_chain,
}

async def route_file_request(session_id: str, text: str) -> str:
    """
    Routes a chat request to the appropriate file agent, passing all files in the session.
    """
    files = get_session_files(session_id)
    if not files:
        return "You haven't uploaded any files yet. Please upload a file first!"

    # Default to fileread agent
    agent_key = "fileread"
    target_agent = FILE_AGENT_REGISTRY[agent_key]
    
    logger.info(f"Routing file chat request | session={session_id} | files={len(files)}")
    return await target_agent(files, text, session_id)
