"""
llm_helper.py
-------------
LangChain-powered helper that manages the full LLM calling structure:
  1. Build a ChatPromptTemplate with a fixed System prompt + dynamic Human prompt.
  2. Pipe it through an LLM chain  (prompt | llm | output_parser).
  3. Return the plain-text AI response.

Usage
-----
from app.modules.gateway_api.helpers.llm_helper import LLMHelper

helper = LLMHelper()
result: str = await helper.invoke("Tell me about quantum computing")
"""

from __future__ import annotations

import logging
from functools import lru_cache

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# System prompt — customise to shape the LLM personality / context
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = (
    "You are Hylifen AI, a knowledgeable and concise assistant. "
    "Your role is to answer questions accurately and helpfully. "
    "Always respond in plain, clear English unless asked to do otherwise. "
    "If you are unsure about something, say so instead of guessing. "
    "IMPORTANT: When a user asks you to create a diagram, flowchart, mind map, or graph, "
    "you MUST output valid Mermaid.js syntax enclosed in a markdown code block labeled `mermaid`. "
    "Do NOT output markdown code blocks for diagrams using any other language. "
    "CRITICAL: Always use valid Mermaid syntax. For flowcharts, use '-->' for links (NOT '->'). "
    "IMPORTANT: When a user asks you to create a table or tabular data, output the data in JSON format "
    "enclosed in a markdown code block labeled `json_table`. "
    "The JSON MUST have this exact structure: {{\"columns\": [\"col1\", \"col2\"], \"rows\": [{{\"col1\": \"val1\", \"col2\": \"val2\"}}]}}."
)



class LLMHelper:
    """
    Encapsulates the LangChain prompt → LLM → parser chain.

    The chain is stateless — each ``invoke`` call is independent.
    The underlying ``ChatOpenAI`` client is shared across calls for
    connection-pool efficiency.
    """

    def __init__(
        self,
        model: str | None = None,
        temperature: float | None = None,
        system_prompt: str = _SYSTEM_PROMPT,
    ) -> None:
        resolved_model = model or settings.OPENAI_MODEL
        resolved_temp = temperature if temperature is not None else settings.OPENAI_TEMPERATURE

        # ── LLM ────────────────────────────────────────────────────────────
        self._llm = ChatOpenAI(
            model=resolved_model,
            temperature=resolved_temp,
            api_key=settings.OPENAI_API_KEY,
        )

        # ── Prompt template ────────────────────────────────────────────────
        # "system"  → fixed instructions injected before every request
        # "human"   → the runtime user message built by the service layer
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{user_message}"),
            ]
        )

        # ── Output parser ──────────────────────────────────────────────────
        # StrOutputParser extracts the plain string from the AIMessage
        self._parser = StrOutputParser()

        # ── Composed LCEL chain ────────────────────────────────────────────
        # prompt | llm | parser  — the canonical LangChain Expression Language pattern
        self._chain = self._prompt | self._llm | self._parser

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    async def invoke(self, user_message: str) -> str:
        """
        Asynchronously invoke the LLM chain.

        Parameters
        ----------
        user_message:
            The fully-formed user prompt (already enriched by the service layer).

        Returns
        -------
        str
            The raw text content of the AI response.
        """
        logger.info("LLMHelper.invoke | model=%s | prompt_len=%d", self._llm.model_name, len(user_message))

        response: str = await self._chain.ainvoke({"user_message": user_message})

        logger.info("LLMHelper.invoke | response_len=%d", len(response))
        return response

    def invoke_sync(self, user_message: str) -> str:
        """
        Synchronous variant — available for scripts / tests that cannot run
        inside an async event loop.
        """
        logger.info("LLMHelper.invoke_sync | model=%s | prompt_len=%d", self._llm.model_name, len(user_message))
        response: str = self._chain.invoke({"user_message": user_message})
        logger.info("LLMHelper.invoke_sync | response_len=%d", len(response))
        return response


# ---------------------------------------------------------------------------
# Module-level singleton — avoids re-creating the client on every request
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_llm_helper() -> LLMHelper:
    """Return the shared ``LLMHelper`` singleton (cached after first call)."""
    return LLMHelper()
