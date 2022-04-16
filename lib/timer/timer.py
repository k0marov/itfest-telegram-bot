"""Module that provides the Timer class"""
import asyncio
from typing import Callable

class Timer:
    """A periodic timer that executes the given callback on the given interval"""
    def __init__(self, duration_minutes: int, callback: Callable[[], None]):
        self.duration = duration_minutes
        self.callback = callback
    async def __repeat(self):
        while True:
            self.callback()
            await asyncio.sleep(self.duration*60)
    def start(self):
        """Starts the timer"""
        asyncio.run(self.__repeat())
