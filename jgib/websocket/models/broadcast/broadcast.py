from pydantic import BaseModel, Field
from enum import Enum


class BroadcastDto(BaseModel):
    channel: str = Field(
        default_factory=lambda: None
    )  # Default is None, will be set in __init__

    def __init__(self, *args, **kwargs):
        # Call the parent's __init__ method to properly handle initialization
        super().__init__(*args, **kwargs)

        # Dynamically set msgType to the subclass name
        self.channel = self.__class__.__name__
