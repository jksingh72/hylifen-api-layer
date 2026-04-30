"""
models.py — Gateway API Pydantic schemas
-----------------------------------------
Defines the request body and response envelope for the
/gateway/process endpoint.
"""

from pydantic import BaseModel, Field


class GatewayRequest(BaseModel):
    """
    Incoming request for the gateway LLM endpoint.

    Attributes
    ----------
    text:
        Raw input text from the caller.  The service layer will
        wrap this in a fully-formed prompt before sending to the LLM.
    context:
        Optional extra context the caller can supply to help the LLM
        (e.g. domain, language, topic area).
    """

    text: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Input text to process through the LLM.",
        examples=["Summarise the key points of quantum entanglement."],
    )
    context: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional domain context to narrow the LLM's focus.",
        examples=["physics", "finance", "healthcare"],
    )


class GatewayResponse(BaseModel):
    """
    Outgoing response from the gateway LLM endpoint.

    Attributes
    ----------
    input_text:
        Echo of the original caller input (useful for debugging / logging).
    output_text:
        The LLM-generated response text.
    model:
        Name of the LLM model that generated the response.
    """

    input_text: str = Field(description="Original input text received.")
    output_text: str = Field(description="AI-generated response text.")
    model: str = Field(description="LLM model used to generate the response.")
