from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser:
    def __init__(self, user_id: str, email: str, name: Optional[str] = None):
        self.user_id = user_id
        self.email = email
        self.name = name


# Returned when AUTH_BYPASS_ENABLED=true — mirrors the React mock session
MOCK_USER = AuthenticatedUser(
    user_id="local-dev-user",
    email="local.user@example.com",
    name="Local Dev User",
)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> AuthenticatedUser:
    # Bypass auth for local development (AUTH_BYPASS_ENABLED=true in .env)
    if settings.AUTH_BYPASS_ENABLED:
        return MOCK_USER

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token = credentials.credentials
        id_info = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
        return AuthenticatedUser(
            user_id=id_info["sub"],
            email=id_info["email"],
            name=id_info.get("name"),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
