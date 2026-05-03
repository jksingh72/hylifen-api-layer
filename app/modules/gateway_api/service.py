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

from app.modules.gateway_api.models import GatewayRequest, GatewayResponse

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Service function
# ---------------------------------------------------------------------------

async def process_text(request: GatewayRequest) -> GatewayResponse:
    """
    Orchestrate the full text-in → Orchestrator → text-out pipeline.

    Parameters
    ----------
    request:
        Validated GatewayRequest from the router.

    Returns
    -------
    GatewayResponse
        Contains the original input text, the AI output text, and the model name.
    """
    from app.modules.gateway_api.orchestrator import route_request
    
    logger.info(
        "GatewayService.process_text | context=%s | text_len=%d",
        request.context,
        len(request.text),
    )

    # Hand off to the Orchestrator (Supervisor Agent)
    output_text = await route_request(request.text, request.context, request.session_id)

    return GatewayResponse(
        input_text=request.text,
        output_text=output_text,
        model=settings.OPENAI_MODEL,
    )
