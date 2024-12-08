from pydantic import BaseModel, ValidationError
from enum import Enum
from typing import Union
import json


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


# Define a union of all possible channels
MessageChannel = Union[Channel.Command, Channel.Data, Channel.Request, Channel.Event]


class MessageDto(BaseModel):
    channel: MessageChannel
