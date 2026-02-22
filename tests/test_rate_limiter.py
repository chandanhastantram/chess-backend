"""Tests for the rate limiter"""
import pytest
import time
from app.middleware.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test the sliding window rate limiter"""

    def test_allows_requests_under_limit(self):
        limiter = RateLimiter(default_limit=5, auth_limit=2, window_seconds=60)
        for _ in range(5):
            assert limiter.is_allowed("192.168.1.1") is True

    def test_blocks_requests_over_limit(self):
        limiter = RateLimiter(default_limit=3, auth_limit=2, window_seconds=60)
        for _ in range(3):
            limiter.is_allowed("192.168.1.1")
        assert limiter.is_allowed("192.168.1.1") is False

    def test_different_ips_tracked_independently(self):
        limiter = RateLimiter(default_limit=2, auth_limit=1, window_seconds=60)
        assert limiter.is_allowed("192.168.1.1") is True
        assert limiter.is_allowed("192.168.1.1") is True
        assert limiter.is_allowed("192.168.1.1") is False  # blocked
        assert limiter.is_allowed("192.168.1.2") is True  # different IP, ok

    def test_auth_endpoint_stricter_limit(self):
        limiter = RateLimiter(default_limit=10, auth_limit=2, window_seconds=60)
        assert limiter.is_allowed("192.168.1.1", is_auth_endpoint=True) is True
        assert limiter.is_allowed("192.168.1.1", is_auth_endpoint=True) is True
        assert limiter.is_allowed("192.168.1.1", is_auth_endpoint=True) is False

    def test_remaining_count(self):
        limiter = RateLimiter(default_limit=5, auth_limit=2, window_seconds=60)
        assert limiter.get_remaining("192.168.1.1") == 5
        limiter.is_allowed("192.168.1.1")
        assert limiter.get_remaining("192.168.1.1") == 4
        limiter.is_allowed("192.168.1.1")
        assert limiter.get_remaining("192.168.1.1") == 3

    def test_auth_remaining_count(self):
        limiter = RateLimiter(default_limit=10, auth_limit=3, window_seconds=60)
        assert limiter.get_remaining("192.168.1.1", is_auth_endpoint=True) == 3
        limiter.is_allowed("192.168.1.1", is_auth_endpoint=True)
        assert limiter.get_remaining("192.168.1.1", is_auth_endpoint=True) == 2

    def test_window_expiration(self):
        limiter = RateLimiter(default_limit=1, auth_limit=1, window_seconds=1)
        assert limiter.is_allowed("192.168.1.1") is True
        assert limiter.is_allowed("192.168.1.1") is False
        # Wait for window to expire
        time.sleep(1.1)
        assert limiter.is_allowed("192.168.1.1") is True
