from pydantic import BaseModel, Field

class TopicRequest(BaseModel):
    """
    Incoming request for the topic agent endpoint.
    """
    text: str = Field(
        ...,
        min_length=1,
        description="The topic, user feedback, or finalized topic to process."
    )
    agent_flag: str = Field(
        ...,
        description="Flag to decide which agent to run: 'subtopics' or 'videos'."
    )
    session_id: str = Field(
        default="default_topic_session",
        max_length=100,
        description="Unique identifier for the user's conversation session to maintain memory."
    )

class TopicResponse(BaseModel):
    """
    Outgoing response from the topic agent endpoint.
    """
    input_text: str = Field(description="Original input text received.")
    output_text: str = Field(description="AI-generated response text (subtopics layout or markdown table of videos).")
    model: str = Field(description="LLM model used to generate the response.")
