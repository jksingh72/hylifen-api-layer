from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("")
async def health_check():
    """Public liveness check — no authentication required."""
    return {"status": "ok", "env": settings.APP_ENV}
