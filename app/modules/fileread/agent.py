"""
File Read Agent
---------------
LangGraph Agent to analyze and read file contents.
"""

from typing import List
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings
from app.modules.filehandler.tools import read_file_content

memory = MemorySaver()

async def fileread_agent_chain(file_paths: List[str], text: str, session_id: str) -> str:
    """
    The LangGraph agent for File Reading, now supporting MULTIPLE FILES.
    """
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)
    
    # List all files for the agent
    file_list_str = "\n".join([f"- {path}" for path in file_paths])
    
    system_prompt = (
        "You are an expert Multi-File Analysis AI. "
        "The user has provided the following files for this session:\n"
        f"{file_list_str}\n\n"
        "Use the 'read_file_content' tool to inspect any of these files as needed. "
        "You can compare files or extract information across multiple documents. "
        "Answer the user's request based on the data in these files."
    )
    
    agent_executor = create_react_agent(
        llm, 
        tools=[read_file_content], 
        prompt=system_prompt,
        checkpointer=memory
    )
    
    try:
        config = {"configurable": {"thread_id": session_id}}
        result = await agent_executor.ainvoke(
            {"messages": [("user", text)]},
            config=config
        )
        return result["messages"][-1].content
    except Exception as e:
        import logging
        logging.error(f"Fileread Agent Execution failed: {e}")
        return f"I encountered an error while analyzing the files: {e}"
