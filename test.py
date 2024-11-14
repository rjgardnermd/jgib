from jgmd.logging import LogLevel, Color, FreeTextLogger
from jgmd.events import EventEmitter, getEmitter, handleError, handleErrorAsync
from jgmd.util import loadEnv
import asyncio
from pydantic import BaseModel

# use the logging module
logger = FreeTextLogger(
    logDirectory="./logs", fileName="logger.log", logLevel=LogLevel.DEBUG
)
logger.clearLog()
logger.logDebug(lambda: f"Hello World:")


# use the events module
def onError(event: str, *args, **kwargs):
    logger.logError(
        lambda: f"An error occurred: {args[0]}",
    )


eventEmitter: EventEmitter = getEmitter("error", onError)


def onTestEvent(event: str, *args, **kwargs):
    logger.logDebug(
        lambda: f"Event {event} emitted w/ args {args} and kwargs {kwargs}!",
        Color.GREEN,
    )
    if True:
        raise Exception("This is a FIRST test error!")


EVENT_NAME = "test"
eventEmitter.on(EVENT_NAME, onTestEvent)
eventEmitter.emit(EVENT_NAME, 1, 2, 3, otherStuff="hello")


@handleError
def trySomething():
    logger.logDebug(lambda: "Trying something...")
    if True:
        raise Exception("This is a SECOND test error!")


@handleErrorAsync
async def trySomethingAsync():
    logger.logDebug(lambda: "Trying something async...")
    if True:
        raise Exception("This is a THIRD test error!")


trySomething()

asyncio.run(trySomethingAsync())


# use the loadEnv utility fxn
class Env(BaseModel):
    logDirectory: str
    logLevel: str
    twsApiIp: str
    twsApiPort: int
    watchlistFile: str
    notificationSoundsFile: str
    defaultThresholdsFile: str
    overrideThresholdsFile: str
    pushoverUserKey: str
    pushoverApiToken: str


# Load config
env_config = loadEnv(Env)

print(env_config)


logger.logDebug(lambda: "End of script.")
