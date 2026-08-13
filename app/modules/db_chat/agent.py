"""
Database Chat Agent
-------------------
Handles natural language queries against the PostgreSQL database.
"""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings
from app.modules.db_chat.tools import get_db_tools

# Consistent with other modules: MemorySaver handles session storage
memory = MemorySaver()

async def db_chat_agent_chain(text: str, context: str | None = None, session_id: str = "default_user_session") -> str:
    """
    The agent executor for database queries, equipped with SQL tools and Memory via LangGraph.
    """
    # 1. Initialize the LLM
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)
    
    # 2. Gather tools
    all_tools = get_db_tools()
    
    # 3. Create the system prompt
    system_prompt = (
        "You are a PostgreSQL Server Administrator and Data Analyst AI. "
        "You have access to the entire database server. "
        "1. TOP LEVEL: Use 'server_list_databases' to see all databases on the server. "
        "2. EXPLORATION: Use 'database_get_schema' to see tables and columns for a specific database. "
        "3. QUERYING: Use 'database_run_query' to fetch data from a specific database. "
        "ALWAYS check the schema of a database before you try to query its tables. "
        "NOTE: If a table is in a custom schema (not 'public'), always use the fully qualified name like 'schema_name.table_name' in your SQL queries. "
        "When the user asks about a different database, simply switch by providing the new database name to the tools. "
        "Format results clearly using markdown tables or bullet points."
    )
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
        # Final AI message content
        return result["messages"][-1].content
    except Exception as e:
        import logging
        logging.error(f"DB Agent Execution failed: {e}")
        return f"I encountered an error while querying the database: {e}"
