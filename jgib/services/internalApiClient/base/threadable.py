import asyncio
import threading
from typing import TYPE_CHECKING, Callable
import asyncio

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop
    from threading import Event, Thread


class Threadable:
    def __init__(self, runFxn: Callable):
        self.runFxn = runFxn
        self.secondsBetweenSends: int = 1
        self._stop_event: Event = threading.Event()
        self.loop: AbstractEventLoop = None
        self.thread: Thread = None

    def start(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._startEventLoop, args=(self.loop,))
        self.thread.start()
        asyncio.run_coroutine_threadsafe(self.runFxn(), self.loop)

    def stop(self):
        self._stop_event.set()
        future = asyncio.run_coroutine_threadsafe(self._preStop(), self.loop)
        future.result()  # Wait for the disconnect to complete
        self.loop.call_soon_threadsafe(self._cancel_all_tasks)

    def _startEventLoop(self, loop: asyncio.AbstractEventLoop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def _cancel_all_tasks(self):
        for task in asyncio.all_tasks(self.loop):
            task.cancel()
        self.loop.call_soon_threadsafe(self.loop.stop)

    async def _preStop(self):
        raise NotImplementedError("preStop method must be implemented in subclass")
