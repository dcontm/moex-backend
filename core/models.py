from typing import List, Any, Optional
from pydantic import BaseModel


class Share(BaseModel):
    figi: str


class ShareInfo(Share):
    ticker: str
    name: str
    total: Optional[int] = 0
    free_float: Optional[float] = 0
    weight: Optional[float] = 0
    coefficient: Optional[float] = 0


class Candle(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float

    class Config:
        orm_mode = True


class ShareCandles(BaseModel):
    candles: List[Any] = []


class SharePrice(BaseModel):
    price: float
    open_day: float


class SharesPriceList(BaseModel):
    price_list: List[SharePrice]
