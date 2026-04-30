from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import AuthenticatedUser, get_current_user
from app.modules.stocks.models import StockPriceResponse

router = APIRouter()

# Hardcoded mock price table — replace with real data source later
MOCK_PRICES: dict[str, float] = {
    "AAPL":  189.30,
    "MSFT":  415.50,
    "GOOGL": 172.10,
    "AMZN":  185.75,
    "TSLA":  175.20,
    "NVDA":  875.40,
    "META":  512.60,
    "NFLX":  628.90,
}


@router.get("/{ticker}", response_model=StockPriceResponse)
async def get_stock_price(
    ticker: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Returns the current price for a given stock ticker.
    Requires authentication (or AUTH_BYPASS_ENABLED=true).

    Example: GET /api/v1/stocks/AAPL
    """
    ticker = ticker.upper()
    price = MOCK_PRICES.get(ticker)

    if price is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker '{ticker}' not found. Available: {list(MOCK_PRICES.keys())}",
        )

    return StockPriceResponse(ticker=ticker, price=price)
