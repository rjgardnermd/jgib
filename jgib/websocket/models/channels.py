from enum import Enum


class Channel(Enum):
    TickerList = "TickerList"
    QualifiedContractList = "QualifiedContractList"
    IbClientEvent = "IbClientEvent"
    IbClientCommand = "IbClientCommand"
