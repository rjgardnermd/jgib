import asyncio
import websockets
from typing import Callable
from jgmd.logging import FreeTextLogger, LogLevel
from jgmd.util import exceptionToStr
from ...models import SubscriptionDto, BroadcastDto, TickerDto


class WebSocketClient:
    def __init__(self, onReceive: Callable[[str], None], logger: FreeTextLogger):
        self.logger = logger
        self.onReceive = onReceive
        self._websocket = None
        self._receive_task = None

    async def connect(self, uri: str):
        """Establish a WebSocket connection and start receiving messages."""
        try:
            self._websocket = await websockets.connect(uri)
        except Exception as e:
            self.logger.logError(
                lambda: f"Error connecting to WebSocket server. Please ensure the server is running. Full error: \n{exceptionToStr(e)}"
            )
            raise
        self.logger.logSuccessful(lambda: "Connected to WebSocket server")
        # Start receiving messages in the background
        self._receive_task = asyncio.create_task(self._receive())

    async def send(self, message: str):
        """Send a message through the WebSocket connection."""
        if self._websocket:
            await self._websocket.send(message)
            self.logger.logDebug(lambda: f"Sent: {message}")
        else:
            self.logger.logError(lambda: "WebSocket not connected. Message not sent.")

    async def close(self):
        """Close the WebSocket connection and cancel the receive task."""
        if self._receive_task:
            self._receive_task.cancel()
            await self._receive_task
            self.logger.logSuccessful(lambda: "Receive task successfully cancelled.")
        if self._websocket:
            await self._websocket.close()
            self.logger.logSuccessful(lambda: "WebSocket connection closed.")

    async def _receive(self):
        """Background task to receive messages."""
        try:
            async for message in self._websocket:
                print(f"Received: {message}")
                self.logger.logDebug(lambda: f"Received: {message}")
                if self.onReceive:
                    if asyncio.iscoroutinefunction(self.onReceive):
                        await self.onReceive(message)
                    else:
                        self.onReceive(message)
        except asyncio.CancelledError:
            self.logger.logError(lambda: "Receiving messages task cancelled.")
            raise
        except Exception as e:
            self.logger.logError(lambda: f"Error while receiving messages: {e}")


def jbg(message):
    print(f"JBG: {message}")


async def run():
    logger = FreeTextLogger(
        logDirectory="logs",
        fileName="websocket_client.log",
        logLevel=LogLevel.DEBUG,
    )
    client = WebSocketClient(onReceive=jbg, logger=logger)
    try:
        await client.connect("ws://localhost:8765")
        client.onReceive = jbg
        count = 0
        direction = 1  # 1 for counting up, -1 for counting down

        while True:
            # Simulate doing some work
            print(f"Doing other stuff... Count is {count}")

            # subscribe to a channel
            await client.send(
                SubscriptionDto(
                    action="subscribe", channel="TickerDto"
                ).model_dump_json()
            )
            # Send a message
            # await client.send(f"Count: {count}")

            # broadcast a message
            await client.send(
                TickerDto(conId=1, symbol="AAPL", last=100.0).model_dump_json()
            )
            # Adjust count
            count += direction
            if count == 1_000_000 or count == 0:
                direction *= -1

            # Simulate doing more work
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Main task cancelled.")
    finally:
        await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Program terminated.")
