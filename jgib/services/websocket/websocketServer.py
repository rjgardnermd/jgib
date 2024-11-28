import asyncio
import websockets
from jgmd.logging import FreeTextLogger, LogLevel
from pydantic import ValidationError
from typing import Any
import json
from ...models import (
    SubscriptionDto,
    BroadcastDto,
    TickerDto,
)  # Assume your DTOs are in a `models` module


class WebSocketServer:
    def __init__(self, logger: FreeTextLogger):
        self.logger = logger
        self.channel_subscriptions = {}  # Maps channel names to sets of clients

    async def handle_client(self, websocket):
        self.logger.logSuccessful(
            lambda: f"New client connected: {websocket.remote_address}"
        )

        try:
            async for message in websocket:
                self.logger.logDebug(
                    lambda: f"Received message from {websocket.remote_address}: {message}"
                )
                try:
                    # Determine message type and process accordingly
                    parsed_message = self.parse_message(message)
                    if isinstance(parsed_message, SubscriptionDto):
                        await self.handle_subscription(parsed_message, websocket)
                    elif isinstance(parsed_message, BroadcastDto):
                        await self.handle_broadcast(parsed_message)
                    else:
                        await websocket.send(
                            json.dumps({"error": "Unknown message type"})
                        )
                except ValidationError as e:
                    await websocket.send(json.dumps({"error": str(e)}))
        except websockets.exceptions.ConnectionClosed:
            self.logger.logSuccessful(
                lambda: f"Client disconnected: {websocket.remote_address}"
            )
        finally:
            self.remove_client_from_all_channels(websocket)

    def parse_message(self, message: str) -> Any:
        """Parse a JSON message and validate its type."""
        data = json.loads(message)
        if "action" in data:  # a SubscriptionDto
            return SubscriptionDto(**data)
        else:
            # should be a BroadcastDto
            channel = data.get("channel", None)
            if channel == "TickerDto":
                return TickerDto(**data)

            return BroadcastDto(**data)

    async def handle_subscription(self, dto: SubscriptionDto, websocket):
        """Handle subscription and unsubscription requests."""
        if dto.action == "subscribe":
            self.subscribe_client(dto.channel, websocket)
        elif dto.action == "unsubscribe":
            self.unsubscribe_client(dto.channel, websocket)

    def subscribe_client(self, channel: str, websocket):
        """Add a client to a channel subscription."""
        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = set()
        self.channel_subscriptions[channel].add(websocket)
        self.logger.logDebug(lambda: f"Client subscribed to channel: {channel}")

    def unsubscribe_client(self, channel: str, websocket):
        """Remove a client from a channel subscription."""
        if channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].discard(websocket)
            if not self.channel_subscriptions[channel]:
                del self.channel_subscriptions[channel]
            self.logger.logDebug(lambda: f"Client unsubscribed from channel: {channel}")

    def remove_client_from_all_channels(self, websocket):
        """Remove a client from all channel subscriptions."""
        for channel in list(self.channel_subscriptions.keys()):
            self.unsubscribe_client(channel, websocket)

    async def handle_broadcast(self, dto: BroadcastDto):
        """Broadcast a message to all clients subscribed to a specific channel."""
        self.logger.logDebug(lambda: f"Broadcasting message: {dto}")
        channel = dto.channel
        if channel in self.channel_subscriptions:
            self.logger.logDebug(lambda: f"Broadcasting to channel: {channel}")
            for client in self.channel_subscriptions[channel]:
                try:
                    await client.send(dto.model_dump_json())
                except websockets.exceptions.ConnectionClosed:
                    self.unsubscribe_client(channel, client)

    async def start(self, host="localhost", port=8765):
        """Start the WebSocket server."""
        server = await websockets.serve(self.handle_client, host, port)
        self.logger.logSuccessful(
            lambda: f"WebSocket server started on ws://{host}:{port}"
        )
        await server.wait_closed()


if __name__ == "__main__":
    logger = FreeTextLogger(
        logDirectory="logs", fileName="websocket_server.log", logLevel=LogLevel.DEBUG
    )
    server = WebSocketServer(logger)
    asyncio.run(server.start("localhost", 8765))
