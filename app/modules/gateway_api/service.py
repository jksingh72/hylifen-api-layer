"""
service.py — Gateway API business / prompt-building layer
----------------------------------------------------------
Responsible for:
  1. Receiving the raw caller text and optional context.
  2. Constructing a well-formed user prompt (the "prompt engineering" step).
  3. Delegating to LLMHelper for the actual LLM call.
  4. Returning the structured GatewayResponse.

Keeping prompt logic here (not inside the helper) means:
  - The helper stays a thin, reusable LLM wrapper.
  - Prompt strategy can evolve independently of the HTTP layer.
"""

from __future__ import annotations

import logging

from app.core.config import settings
from app.modules.gateway_api.helpers.llm_helper import LLMHelper, get_llm_helper
from app.modules.gateway_api.models import GatewayRequest, GatewayResponse

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_user_prompt(request: GatewayRequest) -> str:
    """
    Construct the final user-facing prompt string from the caller's input.

    The prompt is intentionally simple here — add few-shot examples,
    chain-of-thought instructions, or output formatting directives below
    as the product evolves.

    Parameters
    ----------
    request:
        The validated GatewayRequest object from the HTTP layer.

    Returns
    -------
    str
        Fully composed prompt ready to send to the LLM.
    """
    parts: list[str] = []

    if request.context:
        parts.append(f"[Context: {request.context.strip()}]")
        parts.append("")  # blank line separator

    parts.append(request.text.strip())

    prompt = "\n".join(parts)
    logger.debug("Built user prompt (len=%d): %s", len(prompt), prompt[:120])
    return prompt


# ---------------------------------------------------------------------------
# Service function
# ---------------------------------------------------------------------------

async def process_text(request: GatewayRequest, helper: LLMHelper | None = None) -> GatewayResponse:
    """
    Orchestrate the full text-in → LLM → text-out pipeline.

    Parameters
    ----------
    request:
        Validated GatewayRequest from the router.
    helper:
        Optional injected LLMHelper (defaults to module singleton).
        Passing a custom helper makes unit-testing easy without patching globals.

    Returns
    -------
    GatewayResponse
        Contains the original input text, the AI output text, and the model name.
    """
    if helper is None:
        helper = get_llm_helper()

    user_prompt = _build_user_prompt(request)

    logger.info(
        "GatewayService.process_text | context=%s | text_len=%d",
        request.context,
        len(request.text),
    )

    output_text = await helper.invoke(user_prompt)

    return GatewayResponse(
        input_text=request.text,
        output_text=output_text,
        model=settings.OPENAI_MODEL,
    )
