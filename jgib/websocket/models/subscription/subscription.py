from pydantic import BaseModel
from enum import Enum


class SubscriptionAction(Enum):
    SUBSCRIBE = "Subscribe"
    UNSUBSCRIBE = "Unsubscribe"


class SubscriptionDto(BaseModel):
    action: str
    channel: str