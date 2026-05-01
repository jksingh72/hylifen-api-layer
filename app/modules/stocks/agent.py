"""
Stocks Domain Agent
-------------------
Handles financial data, stock queries, and market analysis.
"""

from app.modules.common.llm_helper import get_llm_helper

async def stocks_agent_chain(text: str, context: str | None = None) -> str:
    """
    The LCEL-style chain for stock queries.
    Eventually, this will import functions from app.modules.stocks.service to fetch real data.
    """
    helper = get_llm_helper()
    
    prompt = "You are a Financial Analyst AI. Answer questions about the stock market.\n"
    if context:
        prompt += f"Context: {context}\n"
    prompt += f"User Request: {text}\n"
    
    return await helper.invoke(prompt)
