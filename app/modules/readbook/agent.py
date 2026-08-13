"""
Readbook Agent
--------------
Handles book-reading assistance, analyzing pages, summarization, and interactive book questions.
"""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings

# MemorySaver handles the session storage automatically
memory = MemorySaver()

async def readbook_agent_chain(text: str, context: str | None = None, session_id: str = "default_session") -> str:
    """
    The LangGraph agent for book reading assistance, equipped with MEMORY.
    """
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)
    
    system_prompt = (
        "You are 'readbook', a specialized Reading Companion AI Assistant.\n"
        "Your goal is to help users read, analyze, summarize, and understand books and documents.\n"
        "Answer user questions about the book, chapter, or text they are currently reading.\n"
        "Pay close attention to the context of their reading, be helpful, concise, and academic where appropriate.\n"
        "Remember previous context from this conversation."
    )
    if context:
        system_prompt += f"\nContext: {context}"
        
    # Create the LangGraph Agent
    agent_executor = create_react_agent(
        llm, 
        tools=[], 
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
        logging.error(f"Readbook Agent Execution failed: {e}")
        return f"I encountered an error while processing your request: {e}"
