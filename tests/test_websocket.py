import asyncio
import json
from jgib.websocket.services.websocketClient import WebSocketClient
from jgib.websocket.services.websocketServer import WebSocketServer
from jgib.websocket import (
    SubscriptionDto,
    SubscriptionAction,
    Channel,
    TickerList,
    TickerDto,
)
from jgib.websocket.models.base import Channel
from jgmd.logging import FreeTextLogger, LogLevel


testPassed = False
logger = FreeTextLogger("./logs", "debug.log", LogLevel.DEBUG)


async def main():
    # Logger setup
    class MockLogger:
        def logDebug(self, message):
            print(f"DEBUG: {message()}")

        def logError(self, message):
            print(f"ERROR: {message()}")

        def logSuccessful(self, message):
            print(f"SUCCESS: {message()}")

    # Server setup
    server = WebSocketServer(logger, secretToken="test_secret", maxMessagesPerMinute=10)
    server_task = asyncio.create_task(server.start("localhost", 8765))
    await asyncio.sleep(1)  # Allow server to start

    try:
        # Client 1 setup
        messages_received_client1 = []

        async def on_receive_client1(message):
            messages_received_client1.append(message)
            print(f"Client 1 received: {message}")

        client1 = WebSocketClient(onReceive=on_receive_client1, logger=logger)
        await client1.connect("ws://localhost:8765?token=test_secret")
        await client1.subscribe(Channel.Data.Tickers)

        # Client 2 setup
        messages_received_client2 = []

        async def on_receive_client2(message):
            messages_received_client2.append(message)
            print(f"Client 2 received: {message}")

        client2 = WebSocketClient(onReceive=on_receive_client2, logger=logger)
        await client2.connect("ws://localhost:8765?token=test_secret")
        await client2.subscribe(Channel.Data.Tickers)

        # Client 1 sends a TickerList message
        ticker_message = TickerList.create(
            [
                TickerDto(conId=1, symbol="AAPL", last=150.0),
                TickerDto(conId=2, symbol="GOOGL", last=2800.0),
            ]
        ).model_dump_json()
        await client1.send(ticker_message)
        await client2.send(ticker_message)
        await client2.send(ticker_message)

        # Wait briefly for messages to propagate
        await asyncio.sleep(1)

        # Validate that Client 2 receives the message from Client 1
        assert len(messages_received_client2) == 1
        received_message = TickerList.model_validate_json(messages_received_client2[0])
        assert len(messages_received_client1) == 2
        assert received_message.tickers[0].symbol == "AAPL"
        assert received_message.channel == "dat@tickers"

        global testPassed
        testPassed = True

    finally:
        # Cleanup
        await client1.close()
        await client2.close()
        server_task.cancel()
        await asyncio.sleep(1)


# Run the test
asyncio.run(main())

assert testPassed

if testPassed:
    logger.logSuccessful(lambda: "Test passed!")
