from enum import Enum
from .base import Channel, MessageDto


class IbClientEventType(Enum):
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
