"""
OCR Text Extraction Agent
--------------------------
Specialized agent for high-fidelity transcription of handwritten or printed documents.
"""

from typing import List
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings
from app.modules.filehandler.tools import read_file_content

memory = MemorySaver()

async def ocrtext_agent_chain(file_paths: List[str], text: str, session_id: str) -> str:
    """
    The LangGraph agent specifically for OCR and Transcription.
    It focuses on digitizing the content of the files provided.
    """
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)
    
    file_list_str = "\n".join([f"- {path}" for path in file_paths])
    
    system_prompt = (
        "You are an expert Transcription and OCR AI. "
        "Your goal is to extract every piece of text from the provided files accurately. "
        "The user has provided the following files:\n"
        f"{file_list_str}\n\n"
        "INSTRUCTIONS:\n"
        "1. Use the 'read_file_content' tool to perform OCR on the files.\n"
        "2. If the text is handwritten, use your context to fix ambiguities (e.g., correcting '1' vs 'l' based on words).\n"
        "3. Preserve the structure of the document (headers, bullet points, paragraphs).\n"
        "4. Return ONLY the full transcription of the document(s). Do not add conversational filler unless necessary for clarification."
    )
    
    agent_executor = create_react_agent(
        llm, 
        tools=[read_file_content], 
        prompt=system_prompt,
        checkpointer=memory
    )
    
    try:
        config = {"configurable": {"thread_id": f"ocr_{session_id}"}}
        result = await agent_executor.ainvoke(
            {"messages": [("user", text or "Please transcribe these documents.")]},
            config=config
        )
        return result["messages"][-1].content
    except Exception as e:
        import logging
        logging.error(f"OCR Agent Execution failed: {e}")
        return f"Error during transcription: {e}"
