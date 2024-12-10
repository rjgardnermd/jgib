from pydantic import BaseModel, ValidationError
from enum import Enum
from typing import Union
import json

"""
Define all possible channels and a base class for all messages sent through the websocket.
"""


# Define a convenient lookup class for all possible channels.
class Channel:
    class Data(str, Enum):
        Tickers = "dat@tickers"
        Contracts = "dat@contracts"

    class Command(str, Enum):
        IbClient = "cmd@ibClient"

    class Request(str, Enum):
        IbClient = "req@ibClient"

    class Event(str, Enum):
        IbClient = "evt@ibClient"


# Define a union of all possible channels. Every channel is of this type (i.e. MessageChannel is the base type, not Channel).
MessageChannel = Union[Channel.Command, Channel.Data, Channel.Request, Channel.Event]


# Define a base class for all messages sent through the websocket. Every message DTO must inherit from MessageDto.
# Therefore, every message DTO must have a channel attribute.
class MessageDto(BaseModel):
    channel: MessageChannel
