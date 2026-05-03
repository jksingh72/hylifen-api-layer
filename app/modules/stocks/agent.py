"""
Stocks Domain Agent
-------------------
Handles financial data, stock queries, and market analysis.
"""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings
from app.modules.stocks.tools import get_live_stock_price, get_mcp_tools

# In LangGraph, MemorySaver handles the session storage automatically
memory = MemorySaver()

async def stocks_agent_chain(text: str, context: str | None = None, session_id: str = "default_user_session") -> str:
    """
    The agent executor for stock queries, now equipped with tools, MCP, and MEMORY via LangGraph.
    """
    # 1. Initialize the LLM
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)
    
    # 2. Gather tools
    local_tools = [get_live_stock_price]
    mcp_tools = await get_mcp_tools()
    all_tools = local_tools + mcp_tools
    
    # 3. Create the system prompt
    system_prompt = "You are a Financial Analyst AI. Use tools to look up real data. Remember previous context."
    if context:
        system_prompt += f" Context: {context}"
        
    # 4. Create the LangGraph React Agent
    agent_executor = create_react_agent(
        llm, 
        tools=all_tools, 
        prompt=system_prompt,
        checkpointer=memory
    )
    
    # 5. Run the executor with the thread_id config for memory
    try:
        config = {"configurable": {"thread_id": session_id}}
        result = await agent_executor.ainvoke(
            {"messages": [("user", text)]},
            config=config
        )
        # LangGraph returns a list of all messages. We just want the final AI message content.
        return result["messages"][-1].content
    except Exception as e:
        import logging
        logging.error(f"Agent Execution failed: {e}")
        return f"I encountered an error while processing your request: {e}"

