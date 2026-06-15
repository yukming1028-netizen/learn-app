"""Rate limiting middleware for auth endpoints."""
import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    _instance = None

    def __init__(self, app, max_requests=10, window_seconds=60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)
        RateLimitMiddleware._instance = self

    def reset(self):
        """Test utility: clear all rate limit counters."""
        self.requests.clear()

    async def dispatch(self, request, call_next):
        protected_paths = ("/api/auth/login", "/api/auth/register")
        if request.url.path not in protected_paths:
            return await call_next(request)

        ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or request.client.host
        )
        now = time.time()
        self.requests[ip] = [t for t in self.requests[ip] if now - t < self.window_seconds]
        if len(self.requests[ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": f"請求過多，請 {self.window_seconds} 秒後再試。"},
            )
        self.requests[ip].append(now)
        return await call_next(request)
