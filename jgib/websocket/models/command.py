from enum import Enum
from .base import Channel, MessageDto

"""
Connected clients can send commands to the ibClient. Commands are used to request specific actions from the ibClient.
"""


class IbClientCommandType(str, Enum):
    RESET_START_PRICES = "ResetStartPrices"  # Reset the start prices of all tickers to the latest price. This sets the reference point for price deviations to "now".


class IbClientCommandDto(MessageDto):
    command: IbClientCommandType

    @classmethod
    def create(cls, command: IbClientCommandType):
        return cls(
            command=command,
            channel=Channel.Command.IbClient,
        )
