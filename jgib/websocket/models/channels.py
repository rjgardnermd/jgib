from enum import Enum


class BroadcastChannel(Enum):
    TickerList = "TickerList"
    QualifiedContractList = "QualifiedContractList"
    IbClientEvent = "IbClientEvent"
    IbClientCommand = "IbClientCommand"
