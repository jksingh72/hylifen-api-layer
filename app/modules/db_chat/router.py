from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import AuthenticatedUser, get_current_user
from app.modules.db_chat.models import DbChatRequest, DbChatResponse
from app.modules.db_chat.service import process_db_chat

router = APIRouter()

@router.post(
    "/process",
    response_model=DbChatResponse,
    summary="Process database chat queries",
    description="Accepts text, queries the PostgreSQL database via an agent, and returns the response.",
)
async def process_db_text(
    request: DbChatRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> DbChatResponse:
    try:
        return await process_db_chat(request)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"DB Chat call failed: {exc}",
        ) from exc
