from jgib.models import ContractMetaData, InHouseApiModel, TickerDto
from pydantic import BaseModel

metaData = ContractMetaData(
    symbol="AAPL",
    secType="STK",
    exchange="SMART",
    multiplier=100,
    monthOfContract="202209",
    tickSize=0.01,
)

print(metaData)
#     symbol: str
# secType: str
# exchange: str
# multiplier: float = None
# monthOfContract: str = None
# tickSize: float = None
