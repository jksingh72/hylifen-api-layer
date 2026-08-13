from fastapi import APIRouter
from app.api.v1.routes import health, example
from app.modules.stocks.router import router as stocks_router
from app.modules.baseApi.router import router as base_api_router
from app.modules.filehandler.router import router as filehandler_router
from app.modules.db_chat.router import router as db_chat_router
from app.modules.topic.router import router as topic_router
from app.modules.rfp.router import router as rfp_router
from app.modules.notes.router import router as notes_router

api_v1_router = APIRouter()

# Register route modules here — add new ones with one include_router() call
api_v1_router.include_router(health.router, prefix="/health", tags=["Health"])
api_v1_router.include_router(example.router, prefix="/example", tags=["Example"])
api_v1_router.include_router(stocks_router, prefix="/stocks", tags=["Stocks"])
api_v1_router.include_router(base_api_router, prefix="/baseApi", tags=["Base API"])
api_v1_router.include_router(filehandler_router, prefix="/filehandler", tags=["File Handler"])
api_v1_router.include_router(db_chat_router, prefix="/dbChat", tags=["Database Chat"])
api_v1_router.include_router(topic_router, prefix="/topic", tags=["Topic Agent"])
api_v1_router.include_router(rfp_router, prefix="/rfp", tags=["RFP/RFI Analysis"])
api_v1_router.include_router(notes_router, prefix="/notes", tags=["Notes"])


