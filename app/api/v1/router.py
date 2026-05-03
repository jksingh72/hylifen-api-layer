from fastapi import APIRouter
from app.api.v1.routes import health, example
from app.modules.stocks.router import router as stocks_router
from app.modules.baseApi.router import router as base_api_router

api_v1_router = APIRouter()

# Register route modules here — add new ones with one include_router() call
api_v1_router.include_router(health.router, prefix="/health", tags=["Health"])
api_v1_router.include_router(example.router, prefix="/example", tags=["Example"])
api_v1_router.include_router(stocks_router, prefix="/stocks", tags=["Stocks"])
api_v1_router.include_router(base_api_router, prefix="/baseApi", tags=["Base API"])
