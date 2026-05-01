"""
HR Domain Agent
---------------
Handles human resources, policy, and organizational queries.
"""

from app.modules.common.llm_helper import get_llm_helper

async def hr_agent_chain(text: str, context: str | None = None) -> str:
    """
    The LCEL-style chain for HR queries.
    Capable of formatting as tables, text, or Mermaid diagrams based on the user's request.
    """
    helper = get_llm_helper()
    
    prompt = """You are a specialized Human Resources AI Assistant.
Your goal is to provide accurate information regarding company policies, org structure, and employee guidelines.

CRITICAL INSTRUCTION:
Pay close attention to HOW the user wants the information formatted.
- If they ask for a 'diagram' or 'chart', you MUST output a valid Mermaid.js diagram block (e.g. ```mermaid ... ```).
- If they ask for a 'table', output a standard Markdown table.
- Otherwise, output clear, structured markdown text.
"""
    if context:
        prompt += f"\nContext: {context}"
        
    prompt += f"\n\nUser Request: {text}"
    
    return await helper.invoke(prompt)
