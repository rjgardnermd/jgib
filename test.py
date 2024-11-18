from jgib.models import (
    QualifiedContractDto,
    QualifiedContractList,
    InHouseApiModel,
    TickerDto,
    Env,
)
from jgib.services import InHouseApiClient
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


def onMessageReceived(eventType: str, data):
    print(f"{eventType}: {data}")


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


inHouseApiService = InHouseApiClient(
    uri=env.internalApiUri,
    msgReceivedEventType="msgReceived",
    debugLogger=debugLogger,
    errorLogger=errorLogger,
)


def onError(eventType: str, data):
    print(f"Error: {data}")


emitter = getEmitter(
    errorEvent="error",
    onError=onError,
)
emitter.on("msgReceived", onMessageReceived)


async def runAsync():
    inHouseApiService.start()
    # sleep 10 seconds
    await asyncio.sleep(1000)
    inHouseApiService.stop()


asyncio.run(runAsync())
