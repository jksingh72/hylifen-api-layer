"""
orchestrator.py — The Supervisor / Router for the Gateway API
-------------------------------------------------------------
This module analyzes the incoming request text and decides which 
Domain Agent should handle it.
"""

from typing import Any
import logging
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from app.core.config import settings
from app.modules.common.llm_helper import get_llm_helper

# Import domain agents
from app.modules.general.agent import general_agent_chain
from app.modules.hr.agent import hr_agent_chain
from app.modules.stocks.agent import stocks_agent_chain

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Agent Registry
# ---------------------------------------------------------------------------
# This registry allows dynamic routing based on descriptions.
AGENT_REGISTRY = {
    "stocks_agent": {
        "description": "Use this agent for questions about finance, stock markets, budgeting, or economic analysis.",
        "chain": stocks_agent_chain
    },
    "hr_agent": {
        "description": "Use this agent for questions about Human Resources, employee policies, or organizational structure.",
        "chain": hr_agent_chain
    },
    "general_agent": {
        "description": "Use this agent for general chat, coding help, or any topic that doesn't fit a specific domain.",
        "chain": general_agent_chain
    }
}

class RouteDecision(BaseModel):
    agent_name: str = Field(
        description="The name of the chosen agent from the registry."
    )

def _build_router_prompt(text: str) -> str:
    agent_descriptions = "\n".join(
        [f"- {name}: {info['description']}" for name, info in AGENT_REGISTRY.items()]
    )
    prompt = f"""
You are a Supervisor Agent. Your job is to analyze the following user input and route it to the appropriate domain agent.

Available Agents:
{agent_descriptions}

User Input:
"{text}"

Which agent should handle this request? Return ONLY the agent name.
"""
    return prompt.strip()

async def route_request(text: str, context: str | None = None, session_id: str = "default_session") -> str:
    """
    Main entry point for the orchestrator.
    Routes the text to the correct domain agent and returns the result.
    """
    helper = get_llm_helper()
    
    # 1. Decide the route
    # (In a production system, we'd use the LLM's structured output / tool calling here.
    # For now, we'll ask the LLM and clean the response).
    router_prompt = _build_router_prompt(text)
    
    logger.info("Orchestrator: Deciding route for text length %d", len(text))
    decision_text = await helper.invoke(router_prompt)
    
    # Simple extraction (assuming LLM follows instructions)
    chosen_agent = "general_agent" # default fallback
    for name in AGENT_REGISTRY.keys():
        if name.lower() in decision_text.lower():
            chosen_agent = name
            break
            
    logger.info("Orchestrator: Selected agent -> %s", chosen_agent)
    
    # 2. Invoke the chosen agent's chain
    target_chain = AGENT_REGISTRY[chosen_agent]["chain"]
    
    # 3. Return the result
    return await target_chain(text, context, session_id)
