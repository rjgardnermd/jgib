# from .eventTypes import EventTypes
from ..util import exceptionToStr
from .eventEmitter import getEmitter


# create handleError decorator
def handleError(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = exceptionToStr(e)
            emitter = getEmitter()
            emitter.emit(emitter.errorEvent, error_message)

    return wrapper


def handleErrorAsync(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_message = exceptionToStr(e)
            emitter = getEmitter()
            emitter.emit(emitter.errorEvent, error_message)

    return wrapper
