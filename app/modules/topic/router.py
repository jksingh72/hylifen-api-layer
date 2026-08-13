from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import AuthenticatedUser, get_current_user
from app.modules.topic.models import TopicRequest, TopicResponse
from app.modules.topic.service import process_topic_request

router = APIRouter()

@router.post(
    "/process",
    response_model=TopicResponse,
    summary="Process topic-related queries (subtopics or YouTube videos search)",
    description="Invokes either the Topic Finalizer Agent or the YouTube Video Search Agent based on the agent_flag parameter.",
)
async def process_topic(
    request: TopicRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> TopicResponse:
    try:
        return await process_topic_request(request)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Topic Agent execution failed: {exc}",
        ) from exc
