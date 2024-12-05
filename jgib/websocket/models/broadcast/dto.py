from typing import Any, List, Set, Optional
from .broadcast import BroadcastDto


class TickerDto(BroadcastDto):
    conId: int
    symbol: Any
    last: float
    startPrice: Optional[float] = None
    pctDeviation: Optional[float] = None


class TickerList(BroadcastDto):
    tickers: List[TickerDto]


class QualifiedContractDto(BroadcastDto):
    conId: int
    symbol: str
    secType: str
    exchange: str
    multiplier: Optional[float] = None
    monthOfContract: Optional[str] = None
    tickSize: Optional[float] = None
    watchlist: Optional[str] = None


class QualifiedContractList(BroadcastDto):
    contracts: List[QualifiedContractDto]
