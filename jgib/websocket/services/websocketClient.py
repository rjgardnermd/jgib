import asyncio
import websockets
import json
from typing import Callable, Dict, Awaitable, List
from jgmd.logging import FreeTextLogger, LogLevel
from jgmd.util import exceptionToStr
from ..models import SubscriptionDto, Channel, SubscriptionAction, MessageDto
from websockets.asyncio.client import ClientConnection


class WebSocketClient:
    def __init__(
        self,
        logger: FreeTextLogger,
        name: str,
    ):
        self._logger = logger
        self._websocket: ClientConnection = None
        self._receive_task = None
        self._name: str = name
        self._messageHandlers: Dict[str, Callable[[Dict], Awaitable[None]]] = {}

    def registerMessageHandlers(
        self, handlers: Dict[str, Callable[[Dict], Awaitable[None]]]
    ):
        """
        Register handlers for specific message channels.
        """
        self._messageHandlers = handlers

    async def subscribeToChannels(self, channels: List[Channel]):
        """
        Subscribe to multiple channels in the WebSocket API.
        """
        tasks = [self.subscribeToChannel(channel) for channel in channels]
        await asyncio.gather(*tasks)
        # self.logger.logSuccessful(lambda: f"Subscribed to channels: {channels}")

    async def subscribeToChannel(self, channel: Channel):
        """Subscribe to a channel."""
        await self.send(
            SubscriptionDto(
                action=SubscriptionAction.SUBSCRIBE.value, channel=channel.value
            )
        )
        self._logger.logSuccessful(
            lambda: f"{self._name} subscribed to {channel.value}"
        )

    async def connect(self, uri: str, token: str):
        """Establish a WebSocket connection and start receiving messages."""
        try:
            uri = f"{uri}?token={token}&name={self._name}"
            self._websocket = await websockets.connect(uri)
        except Exception as e:
            self._logger.logError(
                lambda: f"{self._name} Error connecting to WebSocket server. "
                f"Please ensure the server is running. Full error: \n{exceptionToStr(e)}"
            )
            raise
        self._logger.logSuccessful(
            lambda: f"{self._name} connected to WebSocket server"
        )
        # Start receiving messages in the background
        self._receive_task = asyncio.create_task(self._receive())

    async def send(self, dto: MessageDto):
        """Send a message through the WebSocket connection."""
        try:
            message = dto.model_dump_json()
            if self._websocket:
                await self._websocket.send(message)
                self._logger.logDebug(lambda: f"{self._name} sent: {message}")
            else:
                self._logger.logError(
                    lambda: f"{self._name} WebSocket not connected. Message not sent."
                )
        except Exception as e:
            self._logger.logError(lambda: f"{self._name} Error sending message: {e}")
            raise

    async def close(self):
        """Close the WebSocket connection and cancel the receive task."""
        # Cancel the receive task if it exists and is still running
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
            finally:
                self._logger.logSuccessful(
                    lambda: f"{self._name} Receive task successfully cancelled."
                )

        # Close the WebSocket connection if it's open
        if self._websocket and self._websocket.state <= 1:  # 0 is CONNECTING, 1 is OPEN
            await self._websocket.close()
            self._logger.logSuccessful(
                lambda: f"{self._name} WebSocket connection closed."
            )

    async def _receive(self):
        """Background task to receive messages."""
        try:
            async for message in self._websocket:
                self._logger.logDebug(lambda: f"{self._name} received: {message}")
                data = json.loads(message)
                channel = data.get("channel")

                if channel in self._messageHandlers:
                    handler = self._messageHandlers[channel]
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                else:
                    self._logger.logError(
                        lambda: f"No handler registered for channel: {channel}"
                    )
        except asyncio.CancelledError:
            self._logger.logError(
                lambda: f"{self._name} Receiving messages task cancelled."
            )
            raise
        except Exception as e:
            self._logger.logError(
                lambda: f"{self._name} Error while receiving messages: {e}"
            )
            raise


if __name__ == "__main__":
    import argparse
    from ..models import (
        TickerDto,
        TickerList,
    )

    parser = argparse.ArgumentParser(description="WebSocket client identifier")
    parser.add_argument(
        "--id", type=str, required=True, help="Unique identifier for the client"
    )
    args = parser.parse_args()
    clientId = args.id

    def onTicker(message):
        print(f"JBG: {message}")

    async def run(id: str):
        logger = FreeTextLogger(
            logDirectory="logs",
            fileName="websocket_client.log",
            logLevel=LogLevel.DEBUG,
        )
        client = WebSocketClient(logger=logger, name=f"TestClient_{id}")
        try:
            await client.connect("ws://localhost:8765", token="secret")
            client.registerMessageHandlers(
                {
                    Channel.Data.Tickers: onTicker,
                }
            )
            count = 0
            direction = 1  # 1 for counting up, -1 for counting down

            await client.subscribeToChannel(Channel.Data.Tickers)

            while True:
                print(f"Client {id}: Count is {count}")

                # broadcast a message
                tickerDto = TickerDto(conId=1, symbol=f"AAPL_{id}", last=100.0 + count)
                tickerList = TickerList.create([tickerDto])
                await client.send(tickerList)
                # Adjust count
                count += direction
                if count == 1_000_000 or count == 0:
                    direction *= -1

                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Main task cancelled.")
        finally:
            await client.close()

    try:
        asyncio.run(run(clientId))
    except KeyboardInterrupt:
        print("Program terminated.")
