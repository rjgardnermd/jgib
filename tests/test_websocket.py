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
token = "test_secret"


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
    server = WebSocketServer(logger, secretToken=token, maxMessagesPerMinute=10)
    server_task = asyncio.create_task(server.start("localhost", 8765))
    await asyncio.sleep(1)  # Allow server to start

    try:
        # Client 1 setup
        messages_received_client1 = []

        async def on_receive_client1(message):
            messages_received_client1.append(message)

        client1 = WebSocketClient(logger=logger, name="Client1")
        await client1.connect("ws://localhost:8765", token=token)
        client1.registerMessageHandlers({Channel.Data.Tickers: on_receive_client1})
        await client1.subscribeToChannel(Channel.Data.Tickers)

        # Client 2 setup
        messages_received_client2 = []

        async def on_receive_client2(message):
            messages_received_client2.append(message)

        client2 = WebSocketClient(logger=logger, name="Client2")
        await client2.connect("ws://localhost:8765", token=token)
        client2.registerMessageHandlers({Channel.Data.Tickers: on_receive_client2})
        await client2.subscribeToChannel(Channel.Data.Tickers)

        # Client 1 sends a TickerList message
        ticker_message_from_1 = TickerList.create(
            [
                TickerDto(conId=1, symbol="TSLA", last=111.1),
                TickerDto(conId=2, symbol="MSFT", last=11.11),
            ]
        )
        ticker_message_from_2 = TickerList.create(
            [
                TickerDto(conId=1, symbol="AAPL", last=222.2),
                TickerDto(conId=2, symbol="GOOGL", last=22.22),
            ]
        )
        await client1.send(ticker_message_from_1)
        await client2.send(ticker_message_from_2)
        await client2.send(ticker_message_from_2)

        # Wait briefly for messages to propagate
        await asyncio.sleep(1)

        # Validate that Client 2 receives the message from Client 1
        assert len(messages_received_client2) == 1
        received_message = TickerList(**messages_received_client2[0])
        assert len(messages_received_client1) == 2
        assert received_message.tickers[0].symbol == "TSLA"
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
