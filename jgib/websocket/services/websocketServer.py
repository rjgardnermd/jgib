import asyncio
import websockets
from websockets.asyncio.server import ServerConnection
from websockets.http11 import Request, Response, Headers
from jgmd.logging import FreeTextLogger, LogLevel, Color
from pydantic import ValidationError
from typing import Any, Dict, Set, List
from collections import defaultdict
from datetime import datetime, timedelta
import json
import urllib.parse
from ..models import SubscriptionDto, SubscriptionAction

"""
The WebSocket server is responsible for accepting incoming client connections, managing client subscriptions to
channels, and broadcasting messages to subscribed clients.
"""


class WebSocketServer:
    def __init__(
        self, logger: FreeTextLogger, secretToken: str, maxMessagesPerMinute: int
    ):
        """Initialize the WebSocket server."""
        self.logger = logger
        self.channel_subscriptions: Dict[str, Set[ServerConnection]] = {}
        self.secretToken = secretToken
        self.maxMessagesPerMinute = (
            maxMessagesPerMinute  # Rate limit per client per minute
        )
        self.message_counts: Dict[ServerConnection, List[datetime]] = defaultdict(list)
        self.client_names: Dict[ServerConnection, str] = {}  # Store client names

    async def process_request(
        self, websocket: ServerConnection, request: Request
    ) -> Response:
        """Validate the client's token and capture the client name before completing the handshake."""
        query = websocket.request.path.split("?", 1)[-1]
        params = urllib.parse.parse_qs(query)
        token = params.get("token", [None])[0]
        name = params.get("name", [None])[0]
        if token != self.secretToken or not name:
            self.logger.logError(
                lambda: f"Unauthorized or unnamed client: {websocket.remote_address}"
            )
            return Response(
                401,
                "Unauthorized/Invalid token or missing client name",
                Headers([("Content-Type", "text/plain")]),
            )
        self.client_names[websocket] = name

    async def start(self, host: str = "localhost", port: int = 8765):
        """Start the WebSocket server."""
        server = await websockets.serve(
            self.handle_client, host, port, process_request=self.process_request
        )
        self.logger.logSuccessful(
            lambda: f"WebSocket server started on ws://{host}:{port}"
        )
        await server.wait_closed()

    async def handle_client(self, websocket: ServerConnection):
        """Handle client connections and manage incoming messages."""
        client_name = self.client_names.get(websocket, "Unknown")
        self.logger.logSuccessful(
            lambda: f"New client connected: {client_name} ({websocket.remote_address})"
        )

        try:
            async for message in websocket:
                if not self.allow_message(websocket):
                    self.logger.logError(
                        lambda: f"Rate limit exceeded for client {client_name}"
                    )
                    await websocket.close(code=4002, reason="Rate limit exceeded")
                    break

                self.logger.logDebug(
                    lambda: f"Received message from {client_name}: {message}"
                )
                try:
                    data: Dict = json.loads(message)
                    if "action" in data:
                        subscriptionDto = SubscriptionDto(**data)
                        await self.handle_subscription(subscriptionDto, websocket)
                    else:
                        channel = data.get("channel")
                        await self.handle_broadcast(channel, message, websocket)
                except ValidationError as e:
                    await websocket.send(json.dumps({"error": str(e)}))
        except websockets.exceptions.ConnectionClosed:
            self.logger.logSuccessful(lambda: f"Client disconnected: {client_name}")
        finally:
            self.remove_client_from_all_channels(websocket)
            self.client_names.pop(websocket, None)
            if websocket in self.message_counts:
                del self.message_counts[websocket]

    def allow_message(self, websocket: ServerConnection) -> bool:
        """Check if a client is within the allowed message rate."""
        now = datetime.now()
        timestamps = self.message_counts[websocket]

        # Remove outdated timestamps (older than 1 minute)
        self.message_counts[websocket] = [
            ts for ts in timestamps if now - ts <= timedelta(minutes=1)
        ]

        # Allow message if under the limit
        if len(self.message_counts[websocket]) < self.maxMessagesPerMinute:
            self.message_counts[websocket].append(now)
            return True
        return False

    async def handle_broadcast(self, channel: str, msg: str, sender: ServerConnection):
        """Broadcast a message to all clients subscribed to a specific channel."""
        sender_name = self.client_names.get(sender, "Unknown")
        self.logger.logDebug(
            lambda: f"Broadcasting message from {sender_name}: {msg}", Color.CYAN
        )
        if channel in self.channel_subscriptions:
            for client in self.channel_subscriptions[channel]:
                try:
                    if client != sender:
                        await client.send(msg)
                except websockets.exceptions.ConnectionClosed:
                    self.unsubscribe_client(channel, client)

    async def handle_subscription(
        self, dto: SubscriptionDto, websocket: ServerConnection
    ):
        """Process subscription or unsubscription requests."""
        if dto.action == SubscriptionAction.SUBSCRIBE.value:
            self.subscribe_client(dto.channel, websocket)
        elif dto.action == SubscriptionAction.UNSUBSCRIBE.value:
            self.unsubscribe_client(dto.channel, websocket)

    def subscribe_client(self, channel: str, websocket: ServerConnection):
        """Add a client to a channel."""
        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = set()
        self.channel_subscriptions[channel].add(websocket)
        self.logger.logSuccessful(
            lambda: f"{self.client_names[websocket]} subscribed to {channel}"
        )

    def unsubscribe_client(self, channel: str, websocket: ServerConnection):
        """Remove a client from a channel."""
        if channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].discard(websocket)
            if not self.channel_subscriptions[channel]:
                del self.channel_subscriptions[channel]
        self.logger.logSuccessful(
            lambda: f"{self.client_names[websocket]} unsubscribed from {channel}"
        )

    def remove_client_from_all_channels(self, websocket: ServerConnection):
        """Remove a client from all subscribed channels."""
        for channel, subscribers in self.channel_subscriptions.items():
            if websocket not in subscribers:
                continue
            subscribers.remove(websocket)
            self.logger.logSuccessful(
                lambda: f"{self.client_names[websocket]} unsubscribed from {channel}"
            )


if __name__ == "__main__":
    logger = FreeTextLogger(
        logDirectory="logs", fileName="websocket_server.log", logLevel=LogLevel.DEBUG
    )
    server = WebSocketServer(logger, secretToken="secret", maxMessagesPerMinute=62)
    asyncio.run(server.start("localhost", 8765))
