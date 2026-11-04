import asyncio
import time

import pytest

from backend.app.errors import AppError
from backend.app.normalisation import normalise_security_text
from backend.app.security import InferenceGate, SlidingWindowRateLimiter


def test_normalisation_removes_evasion_characters():
    attacked = "Ｃоmprеhеnsіve\u200b\u00a0analysis"
    assert normalise_security_text(attacked) == "Comprehensive analysis"


@pytest.mark.asyncio
async def test_inference_gate_rejects_excess_work_with_503():
    gate = InferenceGate(capacity=1, queue_timeout=0.01, inference_timeout=1)
    entered = asyncio.Event()
    release = asyncio.Event()
    loop = asyncio.get_running_loop()

    def slow():
        loop.call_soon_threadsafe(entered.set)
        while not release.is_set():
            time.sleep(0.002)
        return "done"

    first = asyncio.create_task(gate.run_sync(slow))
    await entered.wait()
    with pytest.raises(AppError) as captured:
        await gate.run_sync(slow)
    assert captured.value.status_code == 503
    assert captured.value.code == "SERVER_BUSY"
    release.set()
    assert await first == "done"


@pytest.mark.asyncio
async def test_rate_limiter_returns_false_after_limit():
    limiter = SlidingWindowRateLimiter(requests=2, window_seconds=60)
    assert await limiter.allow("client") is True
    assert await limiter.allow("client") is True
    assert await limiter.allow("client") is False


@pytest.mark.asyncio
async def test_inference_timeout_is_safe_503():
    gate = InferenceGate(capacity=1, queue_timeout=0.01, inference_timeout=0.01)

    def too_slow():
        time.sleep(0.1)

    with pytest.raises(AppError) as captured:
        await gate.run_sync(too_slow)
    assert captured.value.code == "INFERENCE_TIMEOUT"
    assert captured.value.status_code == 503

    # The timed-out worker still occupies its slot until it actually exits.
    with pytest.raises(AppError) as busy:
        await gate.run_sync(lambda: "should not run")
    assert busy.value.code == "SERVER_BUSY"
