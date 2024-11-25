import asyncio
import websockets
from typing import Callable


class WebSocketClient:
    def __init__(self):
        self.on_receive: Callable[[str], None] = None
        self._websocket = None
        self._receive_task = None

    async def connect(self, uri: str):
        """Establish a WebSocket connection and start receiving messages."""
        self._websocket = await websockets.connect(uri)
        print("Connected to WebSocket server")
        # Start receiving messages in the background
        self._receive_task = asyncio.create_task(self._receive())

    async def send(self, message: str):
        """Send a message through the WebSocket connection."""
        if self._websocket:
            await self._websocket.send(message)
            print(f"Sent: {message}")
        else:
            print("WebSocket not connected. Message not sent.")

    async def close(self):
        """Close the WebSocket connection and cancel the receive task."""
        if self._receive_task:
            self._receive_task.cancel()
            await self._receive_task
            print("Receive task successfully cancelled.")
        if self._websocket:
            await self._websocket.close()
            print("WebSocket connection closed.")

    async def _receive(self):
        """Background task to receive messages."""
        try:
            async for message in self._websocket:
                print(f"Received: {message}")
                if self.on_receive:
                    self.on_receive(message)
        except asyncio.CancelledError:
            print("Receiving messages task cancelled.")
            raise
        except Exception as e:
            print(f"Error while receiving messages: {e}")


def jbg(message):
    print(f"JBG: {message}")


async def run():
    client = WebSocketClient()
    try:
        await client.connect("ws://localhost:8765")
        client.on_receive = jbg
        count = 0
        direction = 1  # 1 for counting up, -1 for counting down

        while True:
            # Simulate doing some work
            print(f"Doing other stuff... Count is {count}")

            # Send a message
            await client.send(f"Count: {count}")

            # Adjust count
            count += direction
            if count == 1_000_000 or count == 0:
                direction *= -1

            # Simulate doing more work
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        print("Main task cancelled.")
    finally:
        await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Program terminated.")
