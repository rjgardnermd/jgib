from enum import Enum
from .base import Channel, MessageDto


class IbClientDataRequestType(str, Enum):
    CONTRACTS = "Contracts"


class IbClientRequestDto(MessageDto):
    request: IbClientDataRequestType

    @classmethod
    def create(cls, request: IbClientDataRequestType):
        return cls(
            request=request,
            channel=Channel.Request.IbClient,
        )
