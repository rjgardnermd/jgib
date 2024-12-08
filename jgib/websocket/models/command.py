from enum import Enum
from .base import Channel, MessageDto


class IbClientCommandType(Enum):
    RESET_START_PRICES = "ResetStartPrices"


class IbClientCommandDto(MessageDto):
    command: IbClientCommandType

    @classmethod
    def create(cls, command: IbClientCommandType):
        return cls(
            command=command,
            channel=Channel.Command.IbClient,
        )
