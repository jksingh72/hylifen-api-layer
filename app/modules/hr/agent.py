"""
HR Domain Agent
---------------
Handles human resources, policy, and organizational queries.
"""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings

# MemorySaver handles the session storage automatically
memory = MemorySaver()

async def hr_agent_chain(text: str, context: str | None = None, session_id: str = "default_session") -> str:
    """
    The LangGraph agent for HR queries, equipped with MEMORY.
    """
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)
    
    system_prompt = """You are a specialized Human Resources AI Assistant.
Your goal is to provide accurate information regarding company policies, org structure, and employee guidelines.

CRITICAL INSTRUCTION:
Pay close attention to HOW the user wants the information formatted.
- If they ask for a 'diagram' or 'chart', you MUST output a valid Mermaid.js diagram block (e.g. ```mermaid ... ```).
- If they ask for a 'table', output a standard Markdown table.
- Otherwise, output clear, structured markdown text.

Remember previous context from this conversation.
"""
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
        logging.error(f"Agent Execution failed: {e}")
        return f"I encountered an error while processing your request: {e}"
