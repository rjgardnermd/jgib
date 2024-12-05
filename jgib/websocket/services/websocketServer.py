import asyncio
import websockets
from jgmd.logging import FreeTextLogger, LogLevel
from pydantic import ValidationError
from typing import Any, Dict
import json
from ..models import (
    SubscriptionDto,
    SubscriptionAction,
)


class WebSocketServer:
    def __init__(self, logger: FreeTextLogger):
        self.logger = logger
        self.channel_subscriptions = {}  # Maps channel names to sets of clients

    async def start(self, host="localhost", port=8765):
        """Start the WebSocket server."""
        server = await websockets.serve(self.handle_client, host, port)
        self.logger.logSuccessful(
            lambda: f"WebSocket server started on ws://{host}:{port}"
        )
        await server.wait_closed()

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
                    # Determine whether it's a subscription or a broadcast and process accordingly
                    data: Dict = json.loads(message)
                    if "action" in data:
                        # a SubscriptionDto
                        subscriptionDto = SubscriptionDto(**data)
                        await self.handle_subscription(subscriptionDto, websocket)
                    else:
                        # should be a BroadcastDto
                        channel = data.get("channel")
                        await self.handle_broadcast(channel, message, websocket)
                except ValidationError as e:
                    await websocket.send(json.dumps({"error": str(e)}))
        except websockets.exceptions.ConnectionClosed:
            self.logger.logSuccessful(
                lambda: f"Client disconnected: {websocket.remote_address}"
            )
        finally:
            self.remove_client_from_all_channels(websocket)

    async def handle_broadcast(self, channel: str, msg: str, sender):
        """Broadcast a message to all clients subscribed to a specific channel."""
        self.logger.logDebug(lambda: f"Broadcasting message: {msg}")
        # channel = msg.channel
        if channel in self.channel_subscriptions:
            self.logger.logDebug(lambda: f"Broadcasting to channel: {channel}")
            for client in self.channel_subscriptions[channel]:
                try:
                    if client == sender:
                        continue
                    await client.send(msg)
                except websockets.exceptions.ConnectionClosed:
                    self.unsubscribe_client(channel, client)

    async def handle_subscription(self, dto: SubscriptionDto, websocket):
        """Handle subscription and unsubscription requests."""
        if dto.action == SubscriptionAction.SUBSCRIBE.value:
            self.subscribe_client(dto.channel, websocket)
        elif dto.action == SubscriptionAction.UNSUBSCRIBE.value:
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


if __name__ == "__main__":
    logger = FreeTextLogger(
        logDirectory="logs", fileName="websocket_server.log", logLevel=LogLevel.DEBUG
    )
    server = WebSocketServer(logger)
    asyncio.run(server.start("localhost", 8765))