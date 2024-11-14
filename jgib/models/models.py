from pydantic import BaseModel
from typing import Any, List, Set


class Message(BaseModel):
    text: str

    def __str__(self):
        return self.text


class InHouseApiModel(BaseModel):
    msgType: str
    data: Any


class TickerDto(BaseModel):
    conId: int
    symbol: Any
    price: float
    # volume: Any


class TickerList(BaseModel):
    tickers: List[TickerDto]


class ContractMetaData(BaseModel):
    symbol: str
    secType: str
    exchange: str
    multiplier: float = None
    monthOfContract: str = None
    tickSize: float = None


class ContractMetaDataList(BaseModel):
    contracts: List[ContractMetaData]
