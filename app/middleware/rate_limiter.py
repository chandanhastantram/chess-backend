"""In-memory sliding window rate limiter middleware"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time
from typing import Dict, List
from app.config import settings


class RateLimiter:
    """Sliding window rate limiter"""

    def __init__(self, default_limit: int = 100, auth_limit: int = 30, window_seconds: int = 60):
        self.default_limit = default_limit
        self.auth_limit = auth_limit
        self.window_seconds = window_seconds
        # IP -> list of request timestamps
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def _cleanup(self, ip: str):
        """Remove expired timestamps"""
        cutoff = time.time() - self.window_seconds
        self.requests[ip] = [t for t in self.requests[ip] if t > cutoff]

    def is_allowed(self, ip: str, is_auth_endpoint: bool = False) -> bool:
        """Check if request is allowed under rate limit"""
        self._cleanup(ip)
        limit = self.auth_limit if is_auth_endpoint else self.default_limit
        if len(self.requests[ip]) >= limit:
            return False
        self.requests[ip].append(time.time())
        return True

    def get_remaining(self, ip: str, is_auth_endpoint: bool = False) -> int:
        """Get remaining requests in window"""
        self._cleanup(ip)
        limit = self.auth_limit if is_auth_endpoint else self.default_limit
        return max(0, limit - len(self.requests[ip]))


# Global rate limiter instance
rate_limiter = RateLimiter(
    default_limit=getattr(settings, 'RATE_LIMIT_PER_MINUTE', 100),
    auth_limit=getattr(settings, 'AUTH_RATE_LIMIT_PER_MINUTE', 30),
)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that enforces rate limiting per IP"""

    async def dispatch(self, request: Request, call_next):
        # Skip WebSocket and health check
        path = request.url.path
        if path.startswith("/ws/") or path == "/health":
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Determine if this is an auth endpoint
        is_auth = path.startswith("/api/auth/")

        if not rate_limiter.is_allowed(client_ip, is_auth):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": str(rate_limiter.window_seconds)},
            )

        response = await call_next(request)

        # Add rate limit headers
        remaining = rate_limiter.get_remaining(client_ip, is_auth)
        limit = rate_limiter.auth_limit if is_auth else rate_limiter.default_limit
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = f"{rate_limiter.window_seconds}s"

        return response
