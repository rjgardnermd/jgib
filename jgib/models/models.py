from pydantic import BaseModel, Field
from typing import Any, List, Set, Optional
from enum import Enum


# class Message(BaseModel):
#     text: str

#     def __str__(self):
#         return self.text


class InHouseApiModel(BaseModel):
    msgType: str = Field(
        default_factory=lambda: None
    )  # Default is None, will be set in __init__

    def __init__(self, *args, **kwargs):
        # Call the parent's __init__ method to properly handle initialization
        super().__init__(*args, **kwargs)

        # Dynamically set msgType to the subclass name
        self.msgType = self.__class__.__name__


class TickerDto(InHouseApiModel):
    conId: int
    symbol: Any
    last: float
    # volume: Any


class TickerList(InHouseApiModel):
    tickers: List[TickerDto]


class QualifiedContractDto(InHouseApiModel):
    conId: int
    symbol: str
    secType: str
    exchange: str
    multiplier: Optional[float] = None
    monthOfContract: Optional[str] = None
    tickSize: Optional[float] = None


class QualifiedContractList(InHouseApiModel):
    contracts: List[QualifiedContractDto]


class IbClientLifecycleEventType(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTED = "reconnected"
    CYCLE_COMPLETE = "cycleComplete"


class IbClientLifecycleEventDto(InHouseApiModel):
    event: IbClientLifecycleEventType
