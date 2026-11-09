import pytest

pytest.importorskip("fastapi")

from app.core.rate_limit import RateLimiter  # noqa: E402


def test_allows_up_to_limit_then_blocks():
    limiter = RateLimiter(limit=2, window_s=60)
    assert limiter.check("ip") is None
    assert limiter.check("ip") is None
    assert limiter.check("ip") > 0
    assert limiter.check("other-ip") is None
