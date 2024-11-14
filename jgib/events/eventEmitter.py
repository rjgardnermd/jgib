from __future__ import annotations
from typing import Callable, Dict, List
import asyncio
from dataclasses import dataclass
from ..util import exceptionToStr


_emitter: EventEmitter = None


def getEmitter(errorEvent: str = None, onError: Callable = None) -> EventEmitter:
    global _emitter
    if _emitter is None:
        _emitter = EventEmitter(errorEvent)
        if not errorEvent or not onError:
            raise Exception(
                "getEmitter() must be called with errorEvent and onError arguments on first call!"
            )
        _emitter.on(errorEvent, onError)
    return _emitter


@dataclass
class EmissionMetrics:
    numEmissions: int = 0
    numSuccessfulEmissions: int = 0


class EventEmitter:
    _events: Dict[str, List[Callable]]  # instance variable

    def __init__(self, errorEvent: str):
        if _emitter is not None:
            raise Exception(
                "EventEmitter must be a singleton! Use getEmitter() to create/get the instance."
            )
        self._events = {}
        self.errorEvent = errorEvent

    def on(self, event: str, listener: Callable):
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(listener)

    def off(self, event: str, listener: Callable):
        if event in self._events:
            self._events[event].remove(listener)
            if not self._events[event]:  # If the list is empty, remove the event entry
                del self._events[event]

    def _getAwaitableListeners(self, event: str, *args, **kwargs):
        if event in self._events:
            awaitables = []
            errorStrs = []
            for listener in self._events[event]:
                if asyncio.iscoroutinefunction(listener):
                    # collect async awaitables to invoke later
                    awaitables.append(
                        self._async_listener_wrapper(listener, event, *args, **kwargs)
                    )
                else:
                    # immediately invoke non-async functions
                    try:
                        listener(event, *args, **kwargs)
                    except Exception as e:
                        errorStrs.append(exceptionToStr(e))
            if errorStrs:
                self.emit(
                    self.errorEvent,
                    f"Error during '{event}' event emission!\n\t"
                    + "\n\t".join(errorStrs),
                )
            return awaitables

    async def emitAsync(self, event: str, *args, **kwargs):
        awaitables = self._getAwaitableListeners(event, *args, **kwargs)
        if awaitables:
            await asyncio.gather(*awaitables)

    def emit(self, event: str, *args, **kwargs):
        awaitables = self._getAwaitableListeners(event, *args, **kwargs)
        if awaitables:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(asyncio.gather(*awaitables))
            else:
                loop.run_until_complete(asyncio.gather(*awaitables))

    async def _async_listener_wrapper(self, listener, event, *args, **kwargs):
        try:
            await listener(event, *args, **kwargs)
        except Exception as e:
            error_message = exceptionToStr(e)
            self.emit(self.errorEvent, error_message)
