"""Request throttling and bounded inference admission control."""

import asyncio
import time
from collections import defaultdict, deque
from collections.abc import Callable
from typing import TypeVar

from .errors import AppError


T = TypeVar("T")


class SlidingWindowRateLimiter:
    def __init__(self, requests: int, window_seconds: int) -> None:
        self.requests = requests
        self.window_seconds = window_seconds
        self.history: dict[str, deque[float]] = defaultdict(deque)
        self.lock = asyncio.Lock()

    async def allow(self, key: str) -> bool:
        now = time.monotonic()
        async with self.lock:
            entries = self.history[key]
            while entries and entries[0] <= now - self.window_seconds:
                entries.popleft()
            if len(entries) >= self.requests:
                return False
            entries.append(now)
            return True


class InferenceGate:
    def __init__(self, capacity: int, queue_timeout: float, inference_timeout: float) -> None:
        self.semaphore = asyncio.Semaphore(capacity)
        self.queue_timeout = queue_timeout
        self.inference_timeout = inference_timeout

    async def run_sync(self, operation: Callable[[], T]) -> T:
        try:
            await asyncio.wait_for(self.semaphore.acquire(), timeout=self.queue_timeout)
        except TimeoutError as error:
            raise AppError(503, "SERVER_BUSY", "The model is busy. Please retry shortly.") from error
        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(None, operation)
        try:
            try:
                result = await asyncio.wait_for(asyncio.shield(future), timeout=self.inference_timeout)
            except TimeoutError as error:
                # The caller stops waiting, but the worker cannot be killed safely. Keep the
                # slot occupied until it really finishes so repeated timeouts cannot create
                # an unbounded number of background model operations.
                future.add_done_callback(lambda _: self.semaphore.release())
                raise AppError(503, "INFERENCE_TIMEOUT", "The prediction took too long. Please retry.") from error
            except BaseException:
                self.semaphore.release()
                raise
            self.semaphore.release()
            return result
        except asyncio.CancelledError:
            if not future.done():
                future.add_done_callback(lambda _: self.semaphore.release())
            raise
