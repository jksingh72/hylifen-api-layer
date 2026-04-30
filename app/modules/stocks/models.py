from pydantic import BaseModel


class StockPriceResponse(BaseModel):
    ticker: str
    price: float
    currency: str = "USD"
