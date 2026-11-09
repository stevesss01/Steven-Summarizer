"""Simple in-memory, per-client sliding-window rate limiter.

Suitable for a single instance. For several instances, back this with Redis.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from app.core.config import settings

WINDOW_S = 60.0


class RateLimiter:
    def __init__(self, limit: int, window_s: float = WINDOW_S) -> None:
        self.limit = limit
        self.window_s = window_s
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> float | None:
        """Record a hit. Return seconds to wait if the limit is exceeded, else None."""
        now = time.monotonic()
        hits = self._hits[key]
        while hits and now - hits[0] > self.window_s:
            hits.popleft()
        if len(hits) >= self.limit:
            return self.window_s - (now - hits[0])
        hits.append(now)
        if len(self._hits) > 10_000:
            self._evict(now)
        return None

    def _evict(self, now: float) -> None:
        stale = [k for k, v in self._hits.items() if not v or now - v[-1] > self.window_s]
        for key in stale:
            del self._hits[key]


_limiter = RateLimiter(settings.rate_limit_per_minute)


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def enforce_rate_limit(request: Request) -> None:
    """FastAPI dependency for expensive endpoints."""
    if settings.rate_limit_per_minute <= 0:
        return
    wait = _limiter.check(client_ip(request))
    if wait is not None:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Too many requests. Please wait a minute and try again.",
            headers={"Retry-After": str(int(wait) + 1)},
        )
