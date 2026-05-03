"""
General Domain Agent
--------------------
Handles generic requests that don't fall into a specialized domain.
"""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings

# MemorySaver handles the session storage automatically
memory = MemorySaver()

async def general_agent_chain(text: str, context: str | None = None, session_id: str = "default_session") -> str:
    """
    The LangGraph agent for general queries, equipped with MEMORY.
    """
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)
    
    system_prompt = "You are a helpful general-purpose assistant. Pay close attention to previous conversation context."
    if context:
        system_prompt += f" Context: {context}"
        
    # Create the LangGraph Agent (empty tools list since general agent doesn't need specific tools yet)
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
