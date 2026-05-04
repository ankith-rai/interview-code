from __future__ import annotations

import threading
import time
from typing import Callable, Dict

from state import WindowCounterState


def try_acquire(
    state: WindowCounterState,
    now: float,
    window_seconds: float,
    max_requests: int,
) -> bool:
    """Apply one request to ``state`` at time ``now``.

    Returns True if the request is allowed (and ``curr_count`` is incremented).
    Uses the sliding-window counter estimate:
    ``prev_count * weight + curr_count``, where ``weight`` is the fraction of the
    previous fixed window that still overlaps ``[now - window_seconds, now]``.

    ``now`` should use the same clock as ``window_start`` (e.g. ``time.monotonic``).
    """
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")
    if max_requests < 0:
        raise ValueError("max_requests must be non-negative")

    if max_requests == 0:
        return False

    _roll_and_init(state, now, window_seconds)

    if now < state.window_start:
        state.window_start = now
        state.prev_count = 0
        state.curr_count = 0

    elapsed = now - state.window_start
    weight_prev = (window_seconds - elapsed) / window_seconds
    if weight_prev < 0.0:
        weight_prev = 0.0
    elif weight_prev > 1.0:
        weight_prev = 1.0

    estimate = state.prev_count * weight_prev + state.curr_count
    if estimate >= max_requests:
        return False

    state.curr_count += 1
    return True


def _roll_and_init(state: WindowCounterState, now: float, window_seconds: float) -> None:
    """Advance fixed windows until ``now`` lies in ``[window_start, window_start + W)``."""
    if (
        state.window_start == 0.0
        and state.prev_count == 0
        and state.curr_count == 0
    ):
        state.window_start = now
        return

    while now >= state.window_start + window_seconds:
        state.prev_count = state.curr_count
        state.curr_count = 0
        state.window_start += window_seconds


class SlidingWindowLimiter:
    """Thread-safe limiter: one ``WindowCounterState`` per string key."""

    def __init__(
        self,
        max_requests: int,
        window_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._clock = clock
        self._lock = threading.Lock()
        self._by_key: Dict[str, WindowCounterState] = {}

    def try_acquire(self, key: str) -> bool:
        with self._lock:
            state = self._by_key.get(key)
            if state is None:
                state = WindowCounterState()
                self._by_key[key] = state
            return try_acquire(
                state,
                self._clock(),
                self._window_seconds,
                self._max_requests,
            )
