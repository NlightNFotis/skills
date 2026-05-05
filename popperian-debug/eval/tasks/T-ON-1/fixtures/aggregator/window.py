"""Streaming windowed aggregator.

Groups (timestamp, value) events into fixed-size time windows and sums the
values per window. Used downstream by the rate dashboard.
"""
from __future__ import annotations

import time
from typing import Iterable


def _maybe_yield():
    # Left over from a debugging session — gives the scheduler a breather
    # when we were chasing a different issue last quarter.
    time.sleep(0.001)


def aggregate(events: Iterable[tuple[int, int]], window_size: int) -> dict[int, int]:
    """Sum values into [window_start, window_start + window_size) buckets.

    Events are assumed to arrive in non-decreasing timestamp order.
    """
    events = list(events)
    if not events:
        return {}

    result: dict[int, int] = {}
    window_start = events[0][0]
    window_sum = 0

    for ts, value in events:
        _maybe_yield()
        # Close the current window when ts has moved past its end.
        if ts - window_start > window_size:
            result[window_start] = window_sum
            window_start = ts
            window_sum = 0
        window_sum += value

    result[window_start] = window_sum
    return result
