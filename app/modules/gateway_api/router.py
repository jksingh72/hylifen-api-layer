"""
router.py — Gateway API FastAPI router
---------------------------------------
Exposes a single POST /process endpoint:
  - Accepts: GatewayRequest  { text, context? }
  - Returns: GatewayResponse { input_text, output_text, model }

Authentication is enforced via the shared get_current_user dependency
(same pattern as every other module in this project).
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import AuthenticatedUser, get_current_user
from app.modules.gateway_api.models import GatewayRequest, GatewayResponse
from app.modules.gateway_api.service import process_text

router = APIRouter()


@router.post(
    "/process",
    response_model=GatewayResponse,
    summary="Process text through the LLM gateway",
    description=(
        "Accepts plain text (and an optional domain context), builds a prompt, "
        "sends it to the configured OpenAI model via LangChain, "
        "and returns the AI-generated response."
    ),
)
async def process_gateway_text(
    request: GatewayRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> GatewayResponse:
    """
    **Text-in → LLM → Text-out** endpoint.

    - `text`    — required, max 4 000 characters
    - `context` — optional, narrows the LLM's focus (e.g. "finance", "physics")

    Example request body:
    ```json
    {
        "text": "Explain the Black-Scholes pricing model in simple terms.",
        "context": "finance"
    }
    ```
    """
    try:
        return await process_text(request)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM call failed: {exc}",
        ) from exc
