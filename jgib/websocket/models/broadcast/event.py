from enum import Enum
from .broadcast import BroadcastDto


class IbClientEventType(Enum):
    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"
    RECONNECTED = "Reconnected"
    CYCLE_COMPLETE = "CycleComplete"


class IbClientEventDto(BroadcastDto):
    event: IbClientEventType
