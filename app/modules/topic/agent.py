"""
Topic Agent Module
-------------------
Contains:
1. Topic Finalizer Agent: Used to iteratively finalize a topic of interest by suggesting subtopics.
2. YouTube Video Search Agent: Used to search YouTube videos for a finalized topic and return them in a specific format.
"""

import logging
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings
from app.modules.topic.tools import search_youtube_videos

logger = logging.getLogger(__name__)

# Independent MemorySavers for session context persistence
finalizer_memory = MemorySaver()
youtube_memory = MemorySaver()

async def topic_finalizer_agent_chain(text: str, session_id: str = "default_topic_session") -> str:
    """
    Interactively helps the user find subtopics and finalize their topic of interest.
    """
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)
    
    system_prompt = (
        "You are a Topic Finalization Agent. The user wants to choose and finalize a specific topic of interest.\n"
        "1. When the user sends a topic or interest, analyze it and generate 4-6 distinct, interesting subtopics.\n"
        "2. Present the subtopics in a clear list and wrap each suggested subtopic option in single backticks (e.g. `Machine Learning` or `Neural Networks`) so they can be clicked by the user to finalize instantly. Do NOT include numbers, bullet symbols, or punctuation inside the backticks, only the clean subtopic name itself.\n"
        "3. Ask the user which subtopic they are interested in, or if they want to modify/add options.\n"
        "4. Provide guidance and interact over multiple turns until they select and finalize a single topic.\n"
        "5. Be encouraging, concise, and structured. Always keep track of the conversation memory."
    )
    
    agent_executor = create_react_agent(
        llm,
        tools=[],  # No tools needed for brainstorming subtopics
        prompt=system_prompt,
        checkpointer=finalizer_memory
    )
    
    try:
        config = {"configurable": {"thread_id": f"finalizer_{session_id}"}}
        result = await agent_executor.ainvoke(
            {"messages": [("user", text)]},
            config=config
        )
        return result["messages"][-1].content
    except Exception as e:
        logger.error(f"Topic Finalizer Agent execution failed: {e}")
        return f"Error finalizing topic: {e}"

async def youtube_search_agent_chain(text: str, session_id: str = "default_topic_session") -> str:
    """
    Takes a finalized topic, searches YouTube, and returns videos formatted as: Sl. No., link-header, url.
    """
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)
    
    system_prompt = (
        "You are a YouTube Search Agent. Your job is to:\n"
        "1. Take the user's finalized topic.\n"
        "2. Query the 'search_youtube_videos' tool to find relevant videos.\n"
        "3. Format and return the videos strictly as a Markdown table with the columns: 'Sl. No.', 'link-header', and 'url'.\n"
        "4. In the table, 'link-header' must be the video's title (formatted as a clickable link using its URL if possible), and 'url' must be the plain video URL.\n"
        "5. Do NOT include conversational greetings, explanations, or text other than the Markdown table. Return only the table."
    )
    
    agent_executor = create_react_agent(
        llm,
        tools=[search_youtube_videos],
        prompt=system_prompt,
        checkpointer=youtube_memory
    )
    
    try:
        config = {"configurable": {"thread_id": f"youtube_{session_id}"}}
        result = await agent_executor.ainvoke(
            {"messages": [("user", text)]},
            config=config
        )
        return result["messages"][-1].content
    except Exception as e:
        logger.error(f"YouTube Search Agent execution failed: {e}")
        return f"Error finding YouTube videos: {e}"
