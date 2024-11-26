from jgib.models import (
    QualifiedContractDto,
    QualifiedContractList,
    InHouseApiModel,
    TickerDto,
    Env,
)
from jgib.services import WebSocketClient
from jgmd.util import loadEnv
from jgmd.logging import FreeTextLogger
from jgmd.events import getEmitter, handleError
from pydantic import BaseModel
import asyncio
import time

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


def onMessageReceived(msg: str):
    print(f"Message received: {msg}")


env = loadEnv(Env)
debugLogger = FreeTextLogger(
    logDirectory=env.logDirectory,
    fileName="debug.log",
    logLevel=env.logLevel,
)
errorLogger = FreeTextLogger(
    logDirectory=env.logDirectory,
    fileName="error.log",
    logLevel=env.logLevel,
)


inHouseApiService = WebSocketClient(onMessageReceived, debugLogger)
# inHouseApiService.onReceive = onMessageReceived


def onError(eventType: str, data):
    print(f"Error: {data}")


emitter = getEmitter(
    errorEvent="error",
    onError=onError,
)


async def runAsync():
    await inHouseApiService.connect(
        uri=env.internalApiUri,
    )
    # sleep 10 seconds
    for i in range(1000):
        print(f"Sleeping for {i} seconds")
        await inHouseApiService.send(f"This is a msg {i}")
        await asyncio.sleep(1)

    # await asyncio.sleep(1000)
    await inHouseApiService.close()


asyncio.run(runAsync())
