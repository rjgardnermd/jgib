import asyncio
import websockets
from typing import Callable
from jgmd.logging import FreeTextLogger, LogLevel
from jgmd.util import exceptionToStr
from ...models import SubscriptionDto, TickerDto, TickerList, Channel


class WebSocketClient:
    def __init__(self, onReceive: Callable[[str], None], logger: FreeTextLogger):
        self.logger = logger
        self.onReceive = onReceive
        self._websocket = None
        self._receive_task = None

    async def subscribe(self, channel: Channel):
        """Subscribe to a channel."""
        await self.send(
            SubscriptionDto(action="subscribe", channel=channel.value).model_dump_json()
        )
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





if __name__ == "__main__":
    import argparse

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
            await client.connect("ws://localhost:8765")
            client.onReceive = jbg
            count = 0
            direction = 1  # 1 for counting up, -1 for counting down

            # await client.send(
            #     SubscriptionDto(action="subscribe", channel="TickerList").model_dump_json()
            # )
            await client.subscribe(Channel.TickerList)
            
            while True:
                print(f"Client {id}: Count is {count}")

                # broadcast a message
                tickerDto = TickerDto(conId=1, symbol=f"AAPL_{id}", last=100.0 + count)
                tickerList = TickerList(tickers=[tickerDto])
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
