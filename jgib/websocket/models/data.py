from typing import Any, List, Set, Optional
from .base import Channel, MessageDto
from pydantic import BaseModel


class TickerDto(BaseModel):
    conId: int
    symbol: Any
    last: float
    startPrice: Optional[float] = None
    pctDeviation: Optional[float] = None


class TickerList(MessageDto):
    tickers: List[TickerDto]

    @classmethod
    def create(cls, tickers: List[TickerDto]):
        return cls(
            tickers=tickers,
            channel=Channel.Data.Tickers,
        )


class QualifiedContractDto(BaseModel):
    conId: int
    symbol: str
    secType: str
    exchange: str
    multiplier: Optional[float] = None
    monthOfContract: Optional[str] = None
    tickSize: Optional[float] = None
    watchlist: Optional[str] = None


class QualifiedContractList(MessageDto):
    contracts: List[QualifiedContractDto]

    @classmethod
    def create(cls, contracts: List[QualifiedContractDto]):
        return cls(
            contracts=contracts,
            channel=Channel.Data.Contracts,
        )
