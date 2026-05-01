"""
General Domain Agent
--------------------
Handles generic requests that don't fall into a specialized domain.
"""

from app.modules.common.llm_helper import get_llm_helper

async def general_agent_chain(text: str, context: str | None = None) -> str:
    """
    The LCEL-style chain for general queries.
    Currently wrapped in an async function for simplicity.
    """
    helper = get_llm_helper()
    
    prompt = "You are a helpful general-purpose assistant.\n"
    if context:
        prompt += f"Context: {context}\n"
    prompt += f"User Request: {text}\n"
    
    return await helper.invoke(prompt)
