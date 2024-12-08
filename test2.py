from pydantic import BaseModel, ValidationError
from enum import Enum
from typing import Union
import json


class MessageType(str, Enum):
    PUBLISH = "pub"
    COMMAND = "cmd"
    REQUEST = "req"


class Channel:
    class Data(str, Enum):
        Tickers = "dat@tickers"
        Contracts = "dat@contracts"

    class Command(str, Enum):
        IbClient = "cmd@ibClient"
        Notifications = "cmd@notifications"

    class Request(str, Enum):
        IbClient = "req@ibClient"


# Define a union of all possible channels
MessageChannel = Union[Channel.Command, Channel.Data]


class MessageDto(BaseModel):
    type: MessageType
    channel: MessageChannel


class TickerList(MessageDto):
    tickers: list[str]

    @classmethod
    def create(cls, tickers: list[str]):
        return cls(
            tickers=tickers,
            channel=Channel.Data.Tickers,
            type=MessageType.PUBLISH,
        )


# Tests
def run_tests():
    print("Running tests...\n")

    # Test 1: Valid Initialization
    print("Test 1: Valid Initialization")
    ticker = TickerList.create(["AAPL", "GOOGL"])
    print("Ticker tickers:", ticker.tickers)
    print("Ticker channel:", ticker.channel)
    print("Ticker type:", ticker.type)
    assert ticker.channel == Channel.Data.Tickers
    assert ticker.channel.value == "dat@tickers"
    assert ticker.type == MessageType.PUBLISH
    print("Test 1 Passed\n")

    # Test 2: Serialize to JSON
    print("Test 2: Serialize to JSON")
    json_data = ticker.model_dump_json()
    print("Serialized JSON:", json_data)
    assert json.loads(json_data) == {
        "type": "pub",
        "channel": "dat@tickers",
        "tickers": ["AAPL", "GOOGL"],
    }
    print("Test 2 Passed\n")

    # Test 3: Deserialize from JSON
    print("Test 3: Deserialize from JSON")
    parsed = TickerList.model_validate_json(
        '{"type": "pub", "channel": "dat@tickers", "tickers": ["AAPL", "GOOGL"]}'
    )
    print("Parsed TickerList tickers:", parsed.tickers)
    print("Parsed TickerList channel:", parsed.channel)
    print("Parsed TickerList type:", parsed.type)
    assert parsed.channel == Channel.Data.Tickers
    assert parsed.tickers == ["AAPL", "GOOGL"]
    assert parsed.type == MessageType.PUBLISH
    print("Test 3 Passed\n")

    # Test 4: Validation Error on Invalid Channel
    print("Test 4: Validation Error on Invalid Channel")
    try:
        TickerList.model_validate_json(
            '{"type": "pub", "channel": "invalid@channel", "tickers": ["AAPL", "GOOGL"]}'
        )
    except ValidationError as e:
        print("Validation Error:", e)
        assert "channel" in str(e)
    print("Test 4 Passed\n")

    # Test 5: Missing Required Field
    print("Test 5: Missing Required Field")
    try:
        TickerList.model_validate_json('{"type": "pub", "channel": "dat@tickers"}')
    except ValidationError as e:
        print("Validation Error:", e)
        assert "tickers" in str(e)
    print("Test 5 Passed\n")

    # Test 6: Valid Initialization with Enum Comparison
    print("Test 6: Valid Initialization with Enum Comparison")
    print("Ticker channel:", ticker.channel)
    print("Ticker channel.value:", ticker.channel.value)
    print("Ticker type:", ticker.type)
    assert ticker.channel == Channel.Data.Tickers
    assert ticker.channel.value == "dat@tickers"
    assert ticker.channel in Channel.Data
    assert ticker.type == MessageType.PUBLISH
    print("Test 6 Passed\n")

    # Test 7: Correctly Handles Union of Channels
    print("Test 7: Correctly Handles Union of Channels")
    command_message = MessageDto(
        type=MessageType.COMMAND, channel=Channel.Command.IbClient
    )
    print("CommandMessage channel:", command_message.channel)
    print("CommandMessage type:", command_message.type)
    assert command_message.channel == Channel.Command.IbClient
    assert command_message.channel.value == "cmd@ibClient"
    assert command_message.type == MessageType.COMMAND
    print("Test 7 Passed\n")

    # Test 8: String Comparison with Enum
    print("Test 8: String Comparison with Enum")
    assert ticker.channel == "dat@tickers"
    assert ticker.channel.value == "dat@tickers"
    assert Channel.Data.Tickers == "dat@tickers"
    print("Ticker channel == 'dat@tickers' comparison works")
    assert Channel.Command.IbClient == "cmd@ibClient"
    print("Command channel == 'cmd@ibClient' comparison works")
    print("Test 8 Passed\n")

    print("All tests passed!")


# Run the tests
run_tests()
