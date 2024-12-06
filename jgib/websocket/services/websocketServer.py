import asyncio
import websockets
from websockets.asyncio.server import ServerConnection

# from websockets.http11 import Request, Response, Headers
from jgmd.logging import FreeTextLogger, LogLevel
from pydantic import ValidationError
from typing import Any, Dict, Set, List
from collections import defaultdict
from datetime import datetime, timedelta
import json
import urllib.parse
from ..models import SubscriptionDto, SubscriptionAction


# def print_full_type(obj):
#     obj_type = type(obj)
#     full_type = f"{obj_type.__module__}.{obj_type.__qualname__}"
#     print(full_type)


class WebSocketServer:
    def __init__(
        self, logger: FreeTextLogger, secretToken: str, maxMessagesPerMinute: int
    ):
        self.logger = logger
        self.channel_subscriptions: Dict[str, Set[ServerConnection]] = {}
        self.secretToken = secretToken
        self.maxMessagesPerMinute = maxMessagesPerMinute
        self.message_counts: Dict[ServerConnection, List[datetime]] = defaultdict(list)

    # Commented out process_request for future reference
    # async def process_request(self, websocket: ServerConnection, request: Request) -> Response:
    #     """Validate token before completing the WebSocket handshake."""
    #     print_full_type(request)
    #     query = websocket.request.path.split("?", 1)[-1]
    #     params = urllib.parse.parse_qs(query)
    #     token = params.get("token", [None])[0]

    #     if token != self.secretToken:
    #         self.logger.logError(lambda: f"Unauthorized client: {websocket.remote_address}")
    #         return Response(
    #             400,
    #             "Unauthorized/Invalid token",
    #             Headers([("Content-Type", "text/plain")]),
    #         )

    async def start(self, host: str = "localhost", port: int = 8765):
        """Start the WebSocket server."""
        server = await websockets.serve(self.handle_client, host, port)
        self.logger.logSuccessful(
            lambda: f"WebSocket server started on ws://{host}:{port}"
        )
        await server.wait_closed()

    async def handle_client(self, websocket: ServerConnection):
        """Handle WebSocket client connections."""
        # Extract the 'token' query string from the WebSocket request path
        query = websocket.request.path.split("?", 1)[-1]
        params = urllib.parse.parse_qs(query)
        token = params.get("token", [None])[0]

        if token != self.secretToken:
            # unauthorized client
            self.logger.logError(
                lambda: f"Unauthorized client: {websocket.remote_address}"
            )
            await websocket.close(code=4001, reason="Unauthorized/Invalid token")
            return

        # authorized client
        self.logger.logSuccessful(
            lambda: f"New client connected: {websocket.remote_address}"
        )

        try:
            async for message in websocket:
                if not self.allow_message(websocket):
                    self.logger.logError(
                        lambda: f"Message rate limit exceeded for client: {websocket.remote_address}"
                    )
                    await websocket.close(code=4002, reason="Rate limit exceeded")
                    break

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
            if websocket in self.message_counts:
                del self.message_counts[websocket]

    def allow_message(self, websocket: ServerConnection) -> bool:
        """Check if a client is allowed to send a message based on the rate limit."""
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
        self.logger.logDebug(lambda: f"Broadcasting message: {msg}")
        if channel in self.channel_subscriptions:
            self.logger.logDebug(lambda: f"Broadcasting to channel: {channel}")
            for client in self.channel_subscriptions[channel]:
                try:
                    if client == sender:
                        continue
                    await client.send(msg)
                except websockets.exceptions.ConnectionClosed:
                    self.unsubscribe_client(channel, client)

    async def handle_subscription(
        self, dto: SubscriptionDto, websocket: ServerConnection
    ):
        """Handle subscription and unsubscription requests."""
        if dto.action == SubscriptionAction.SUBSCRIBE.value:
            self.subscribe_client(dto.channel, websocket)
        elif dto.action == SubscriptionAction.UNSUBSCRIBE.value:
            self.unsubscribe_client(dto.channel, websocket)

    def subscribe_client(self, channel: str, websocket: ServerConnection):
        """Add a client to a channel subscription."""
        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = set()
        self.channel_subscriptions[channel].add(websocket)
        self.logger.logDebug(lambda: f"Client subscribed to channel: {channel}")

    def unsubscribe_client(self, channel: str, websocket: ServerConnection):
        """Remove a client from a channel subscription."""
        if channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].discard(websocket)
            if not self.channel_subscriptions[channel]:
                del self.channel_subscriptions[channel]
            self.logger.logDebug(lambda: f"Client unsubscribed from channel: {channel}")

    def remove_client_from_all_channels(self, websocket: ServerConnection):
        """Remove a client from all channel subscriptions."""
        for channel in list(self.channel_subscriptions.keys()):
            self.unsubscribe_client(channel, websocket)


if __name__ == "__main__":
    logger = FreeTextLogger(
        logDirectory="logs", fileName="websocket_server.log", logLevel=LogLevel.DEBUG
    )
    server = WebSocketServer(logger, secretToken="secret", maxMessagesPerMinute=10)
    asyncio.run(server.start("localhost", 8765))
