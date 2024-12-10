from enum import Enum
from .base import Channel, MessageDto

"""
ibClient events are sent from ibClient to notify other interested clients of important events, such as ib gateway connection status.
"""


class IbClientEventType(str, Enum):
    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"
    RECONNECTED = "Reconnected"
    CYCLE_COMPLETE = "CycleComplete"


class IbClientEventDto(MessageDto):
    event: IbClientEventType

    @classmethod
    def create(cls, event: IbClientEventType):
        return cls(
            event=event,
            channel=Channel.Event.IbClient,
        )
