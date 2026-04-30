from fastapi import FastAPI
from app.core.config import settings
from app.core.middleware import setup_middleware
from app.api.v1.router import api_v1_router

app = FastAPI(
    title="Hylifen Main Application API",
    version="0.1.0",
    description="API layer for Hylifen Main Application",
)

setup_middleware(app)

app.include_router(api_v1_router, prefix="/api/v1")
