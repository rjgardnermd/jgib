from pydantic import BaseModel, Field
from typing import Any, List, Set, Optional
from enum import Enum


class Channel(Enum):
    TickerList = "TickerList"
    QualifiedContractList = "QualifiedContractList"
    IbClientLifecycleEventDto = "IbClientLifecycleEventDto"


class SubscriptionAction(Enum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


class SubscriptionDto(BaseModel):
    action: str
    channel: str


class BroadcastDto(BaseModel):
    channel: str = Field(
        default_factory=lambda: None
    )  # Default is None, will be set in __init__

    def __init__(self, *args, **kwargs):
        # Call the parent's __init__ method to properly handle initialization
        super().__init__(*args, **kwargs)

        # Dynamically set msgType to the subclass name
        self.channel = self.__class__.__name__


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


class IbClientLifecycleEventType(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTED = "reconnected"
    CYCLE_COMPLETE = "cycleComplete"


class IbClientLifecycleEventDto(BroadcastDto):
    event: IbClientLifecycleEventType
