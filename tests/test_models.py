import pytest
from pydantic import ValidationError
from jgib.websocket.models.base import Channel
from jgib.websocket.models.data import (
    TickerDto,
    TickerList,
    QualifiedContractDto,
    QualifiedContractList,
)
from jgib.websocket.models.command import IbClientCommandDto, IbClientCommandType
from jgib.websocket.models.event import IbClientEventDto, IbClientEventType
from jgib.websocket.models.request import IbClientRequestDto, IbClientDataRequestType


@pytest.mark.parametrize(
    "model_cls, init_kwargs, expected_json",
    [
        # TickerDto
        (
            TickerDto,
            {"conId": 1, "symbol": "AAPL", "last": 150.0},
            {
                "conId": 1,
                "symbol": "AAPL",
                "last": 150.0,
                "pctDeviation": None,
                "startPrice": None,
            },
        ),
        # QualifiedContractDto
        (
            QualifiedContractDto,
            {
                "conId": 123,
                "symbol": "ES",
                "secType": "FUT",
                "exchange": "CME",
                "multiplier": 50,
            },
            {
                "conId": 123,  # Fixed to match init_kwargs
                "symbol": "ES",  # Fixed to match init_kwargs
                "secType": "FUT",
                "exchange": "CME",
                "multiplier": 50,
                "monthOfContract": None,
                "tickSize": None,
                "watchlist": None,
            },
        ),
        # IbClientCommandDto
        (
            IbClientCommandDto,
            {
                "command": IbClientCommandType.RESET_START_PRICES,
                "channel": Channel.Command.IbClient,
            },
            {"command": "ResetStartPrices", "channel": "cmd@ibClient"},
        ),
        # IbClientEventDto
        (
            IbClientEventDto,
            {"event": IbClientEventType.CONNECTED, "channel": Channel.Event.IbClient},
            {"event": "Connected", "channel": "evt@ibClient"},
        ),
        # IbClientRequestDto
        (
            IbClientRequestDto,
            {
                "request": IbClientDataRequestType.CONTRACTS,
                "channel": Channel.Request.IbClient,
            },
            {"request": "Contracts", "channel": "req@ibClient"},
        ),
    ],
)
def test_model_creation(model_cls, init_kwargs, expected_json):
    model_instance = model_cls(**init_kwargs)
    assert model_instance is not None
    assert model_instance.model_dump() == expected_json
    assert (
        model_cls.model_validate_json(model_instance.model_dump_json())
        == model_instance
    )


@pytest.mark.parametrize(
    "model_cls, invalid_kwargs, expected_error_field",
    [
        # TickerDto
        (TickerDto, {"symbol": "AAPL", "last": 150.0}, "conId"),
        # QualifiedContractDto
        (QualifiedContractDto, {"symbol": "ES"}, "conId"),
        # IbClientCommandDto
        (IbClientCommandDto, {"channel": Channel.Command.IbClient}, "command"),
        # IbClientEventDto
        (IbClientEventDto, {"channel": Channel.Event.IbClient}, "event"),
        # IbClientRequestDto
        (IbClientRequestDto, {"channel": Channel.Request.IbClient}, "request"),
    ],
)
def test_invalid_model_data(model_cls, invalid_kwargs, expected_error_field):
    with pytest.raises(ValidationError) as exc_info:
        model_cls(**invalid_kwargs)
    assert expected_error_field in str(exc_info.value)


def test_ticker_list_creation():
    ticker1 = TickerDto(conId=1, symbol="AAPL", last=150.0)
    ticker2 = TickerDto(conId=2, symbol="GOOGL", last=2800.0)
    ticker_list = TickerList.create([ticker1, ticker2])
    assert ticker_list.channel == Channel.Data.Tickers
    assert len(ticker_list.tickers) == 2
    assert ticker_list.tickers[0].symbol == "AAPL"
