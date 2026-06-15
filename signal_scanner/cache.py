"""Tiny thread-safe TTL cache (reused from mcp-factory).

Market data is slow and rate-limited; a short cache means scanning a 30-symbol
watchlist doesn't refetch the same bars seconds apart.
"""
from __future__ import annotations

import threading
import time
from typing import Any, Callable

_lock = threading.Lock()
_store: dict[str, tuple[float, Any]] = {}


def get_or_fetch(key: str, ttl_s: float, fetch: Callable[[], Any]) -> Any:
    now = time.monotonic()
    with _lock:
        hit = _store.get(key)
        if hit is not None and (now - hit[0]) < ttl_s:
            return hit[1]
    value = fetch()
    with _lock:
        _store[key] = (time.monotonic(), value)
    return value


def clear() -> None:
    with _lock:
        _store.clear()
