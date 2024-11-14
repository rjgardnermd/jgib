from jgib.models import (
    QualifiedContractDto,
    QualifiedContractList,
    InHouseApiModel,
    TickerDto,
)
from pydantic import BaseModel

metaData = QualifiedContractDto(
    conId=123,
    symbol="AAPL",
    secType="STK",
    exchange="SMART",
    multiplier=100,
    monthOfContract="202209",
    tickSize=0.01,
)

print(metaData)

tickerDto = TickerDto(conId=123, symbol="AAPL", last=100.0)
print(tickerDto)
