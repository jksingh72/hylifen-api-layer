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

if __name__ == "__main__":
    import sys
    import uvicorn

    # uvicorn's reload mode forces the Selector event loop on Windows, which
    # cannot spawn subprocesses — breaking the rfp module's Claude Agent SDK
    # calls (it spawns the Claude Code CLI as a subprocess). Reload is disabled
    # on Windows so that loop stays Proactor; other platforms keep hot-reload.
    reload_enabled = sys.platform != "win32"
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=reload_enabled)
