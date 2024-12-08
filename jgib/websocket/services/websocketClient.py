import asyncio
import websockets
from typing import Callable
from jgmd.logging import FreeTextLogger, LogLevel
from jgmd.util import exceptionToStr
from ..models import (
    SubscriptionDto,
    Channel,
    SubscriptionAction,
)
from websockets.asyncio.client import ClientConnection


class WebSocketClient:
    def __init__(
        self, onReceive: Callable[[str], None], logger: FreeTextLogger, name: str
    ):
        self.logger = logger
        self.onReceive = onReceive
        self._websocket: ClientConnection = None
        self._receive_task = None
        self._name: str = name

    async def subscribe(self, channel: Channel):
        """Subscribe to a channel."""
        await self.send(
            SubscriptionDto(
                action=SubscriptionAction.SUBSCRIBE.value, channel=channel.value
            ).model_dump_json()
        )
        self.logger.logDebug(lambda: f"{self._name} subscribed to {channel.value}")

    async def connect(self, uri: str, token: str):
        """Establish a WebSocket connection and start receiving messages."""
        try:
            uri = f"{uri}?token={token}&name={self._name}"
            self._websocket = await websockets.connect(uri)
        except Exception as e:
            self.logger.logError(
                lambda: f"{self._name} Error connecting to WebSocket server. "
                f"Please ensure the server is running. Full error: \n{exceptionToStr(e)}"
            )
            raise
        self.logger.logSuccessful(lambda: f"{self._name} connected to WebSocket server")
        # Start receiving messages in the background
        self._receive_task = asyncio.create_task(self._receive())

    async def send(self, message: str):
        """Send a message through the WebSocket connection."""
        try:
            if self._websocket:
                await self._websocket.send(message)
                self.logger.logDebug(lambda: f"{self._name} sent: {message}")
            else:
                self.logger.logError(
                    lambda: f"{self._name} WebSocket not connected. Message not sent."
                )
        except Exception as e:
            self.logger.logError(lambda: f"{self._name} Error sending message: {e}")
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
                self.logger.logSuccessful(
                    lambda: f"{self._name} Receive task successfully cancelled."
                )

        # Close the WebSocket connection if it's open
        if self._websocket and self._websocket.state <= 1:  # 0 is CONNECTING, 1 is OPEN
            await self._websocket.close()
            self.logger.logSuccessful(
                lambda: f"{self._name} WebSocket connection closed."
            )

    async def _receive(self):
        """Background task to receive messages."""
        try:
            async for message in self._websocket:
                self.logger.logDebug(lambda: f"{self._name} received: {message}")
                if self.onReceive:
                    if asyncio.iscoroutinefunction(self.onReceive):
                        await self.onReceive(message)
                    else:
                        self.onReceive(message)
        except asyncio.CancelledError:
            self.logger.logError(
                lambda: f"{self._name} Receiving messages task cancelled."
            )
            raise
        except Exception as e:
            self.logger.logError(
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

    def jbg(message):
        print(f"JBG: {message}")

    async def run(id: str):
        logger = FreeTextLogger(
            logDirectory="logs",
            fileName="websocket_client.log",
            logLevel=LogLevel.DEBUG,
        )
        client = WebSocketClient(onReceive=jbg, logger=logger)
        try:
            await client.connect("ws://localhost:8765?token=secret")
            client.onReceive = jbg
            count = 0
            direction = 1  # 1 for counting up, -1 for counting down

            await client.subscribe(Channel.Data.Tickers)

            while True:
                print(f"Client {id}: Count is {count}")

                # broadcast a message
                tickerDto = TickerDto(conId=1, symbol=f"AAPL_{id}", last=100.0 + count)
                tickerList = TickerList.create([tickerDto])
                await client.send(tickerList.model_dump_json())
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
        asyncio.run(run(args.id))
    except KeyboardInterrupt:
        print("Program terminated.")
