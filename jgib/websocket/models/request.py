from enum import Enum
from .base import Channel, MessageDto

"""
Connected clients can request data from the ibClient. Requests are used to ask for specific data from the ibClient.
"""


class IbClientDataRequestType(str, Enum):
    CONTRACTS = "Contracts"  # Request a list of all qualified contracts. Each client does this at startup.


class IbClientDataRequestDto(MessageDto):
    request: IbClientDataRequestType

    @classmethod
    def create(cls, request: IbClientDataRequestType):
        return cls(
            request=request,
            channel=Channel.Request.IbClient,
        )
