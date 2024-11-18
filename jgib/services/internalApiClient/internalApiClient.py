from pydantic import BaseModel
from jgmd.events import getEmitter, handleError
from jgmd.logging import FreeTextLogger
from .base.websocketClient import WebSocketClient
from jgib.models import InHouseApiModel


class InHouseApiClient(WebSocketClient):
    def __init__(
        self,
        uri: str,
        msgReceivedEventType: str,
        debugLogger: FreeTextLogger,
        errorLogger: FreeTextLogger,
    ):
        super().__init__(uri, debugLogger, errorLogger)
        self.msgReceivedEventType = msgReceivedEventType

    @handleError
    def _onReceive(self, message: str):
        getEmitter().emit(self.msgReceivedEventType, message)

    @handleError
    def send(self, message: BaseModel):
        msgType = type(message).__name__
        internalApiModel = InHouseApiModel(msgType=msgType, data=message)
        super().send(internalApiModel)
