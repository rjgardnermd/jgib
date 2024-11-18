import asyncio
import asyncio
import websockets
from pydantic import BaseModel
from jgmd.util import exceptionToStr
from jgmd.events import handleErrorAsync, handleError
from jgmd.logging import FreeTextLogger, Color
from collections import deque
from .threadable import Threadable


class WebSocketClient(Threadable):
    def __init__(self, uri, debugLogger: FreeTextLogger, errorLogger: FreeTextLogger):
        super().__init__(runFxn=self._connect)
        self.uri = uri
        self.websocket = None
        self.msgsToSend = deque()
        self.debugLogger = debugLogger
        self.errorLogger = errorLogger

    @handleError
    def send(self, message: BaseModel):
        try:
            msg_str = message.model_dump_json()
            self.msgsToSend.append(msg_str)
            self.debugLogger.logInfo(lambda: f"Queued message: {msg_str}")
        except Exception as e:
            errorStr = exceptionToStr(e)
            self.debugLogger.logInfo(
                lambda: f"Error converting message to json:\n{errorStr}"
            )
            raise e

    @handleErrorAsync
    async def _connect(self):
        try:
            self.websocket = await websockets.connect(self.uri)
            self.debugLogger.logSuccessful(lambda: "Connected to WebSocket server")
            await asyncio.gather(self._receiveForever(), self._sendForever())
        except Exception as e:
            self.errorLogger.logError(
                lambda: f"\nError connecting to WebSocket server. Please ensure the internalApiServer is running. The full exception follows:\n",
                color=Color.YELLOW,
            )
            raise e

    @handleErrorAsync
    async def _receiveForever(self):
        try:
            while not self._stop_event.is_set():
                response = await self.websocket.recv()
                self._onReceive(response)
        except websockets.ConnectionClosed as e:
            self.debugLogger.logWarning(
                lambda: "Websocket receive failed. The connection was likely closed or lost."
            )
            raise e

    @handleErrorAsync
    async def _sendForever(self):
        try:
            while not self._stop_event.is_set():
                length = len(self.msgsToSend)
                for _ in range(length):
                    msg = self.msgsToSend.popleft()
                    await self.websocket.send(msg)
                    self.debugLogger.logInfo(lambda: f"Sent message: {msg}")
                await asyncio.sleep(self.secondsBetweenSends)
        except websockets.ConnectionClosed as e:
            errorStr = exceptionToStr(e)
            self.debugLogger.logWarning(lambda: f"Websocket send failed:\n{errorStr}")
            raise e

    @handleErrorAsync
    async def _disconnect(self):
        self.debugLogger.logWarning(lambda: "Disconnected from WebSocket server...")
        if not self.websocket:
            return
        await self.websocket.close()

    @handleErrorAsync
    async def _preStop(self):
        await self._disconnect()
        # self.debugLogger.logWarning(lambda: "Disconnected from WebSocket server.")

    @handleError
    def _onReceive(self, message: str):
        raise NotImplementedError("on_receive method must be implemented in subclass")
