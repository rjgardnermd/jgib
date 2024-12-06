from enum import Enum
from .broadcast import BroadcastDto


class IbClientCommandType(Enum):
    RESET_START_PRICES = "ResetStartPrices"


class IbClientCommandDto(BroadcastDto):
    command: IbClientCommandType
