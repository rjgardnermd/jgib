from pydantic import BaseModel
from enum import Enum

"""
Connected clients can subscribe/unsubscribe to channels on the websocket (pub/sub) to receive messages.
For example, a client can subscribe to the tickers channel to receive real-time ticker data.
"""


class SubscriptionAction(str, Enum):
    SUBSCRIBE = "Subscribe"
    UNSUBSCRIBE = "Unsubscribe"


class SubscriptionDto(BaseModel):
    action: str
    channel: str
