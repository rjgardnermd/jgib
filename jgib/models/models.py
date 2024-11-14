from pydantic import BaseModel
from typing import Any, List, Set, Optional


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
    last: float
    # volume: Any


class TickerList(BaseModel):
    tickers: List[TickerDto]


class QualifiedContractDto(BaseModel):
    conId: int
    symbol: str
    secType: str
    exchange: str
    multiplier: Optional[float] = None
    monthOfContract: Optional[str] = None
    tickSize: Optional[float] = None


class QualifiedContractList(BaseModel):
    contracts: List[QualifiedContractDto]


# class ContractMetaData(BaseModel):
#     symbol: str
#     secType: str
#     exchange: str
#     multiplier: Optional[float] = None
#     monthOfContract: Optional[str] = None
#     tickSize: Optional[float] = None
#     conId: Optional[int] = None


# class ContractMetaDataList(BaseModel):
#     contracts: List[ContractMetaData]
