import logging
from app.core.config import settings
from app.modules.topic.models import TopicRequest, TopicResponse
from app.modules.topic.agent import topic_finalizer_agent_chain, youtube_search_agent_chain

logger = logging.getLogger(__name__)

async def process_topic_request(request: TopicRequest) -> TopicResponse:
    """
    Selects and runs the appropriate agent chain based on request.agent_flag.
    """
    flag = request.agent_flag.lower().strip()
    logger.info(
        "process_topic_request | flag=%s | session_id=%s | text_len=%d",
        flag,
        request.session_id,
        len(request.text)
    )
    
    if flag == "videos":
        output_text = await youtube_search_agent_chain(request.text, request.session_id)
    else:
        # Default or explicit 'subtopics'
        output_text = await topic_finalizer_agent_chain(request.text, request.session_id)
        
    return TopicResponse(
        input_text=request.text,
        output_text=output_text,
        model=settings.OPENAI_MODEL
    )
