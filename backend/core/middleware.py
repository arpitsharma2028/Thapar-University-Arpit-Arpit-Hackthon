"""
FinSight AI — Production Security & Telemetry Middleware
Enforces defense-in-depth security headers, client rate limiting, request size caps, and correlation IDs.
"""

import time
import uuid
import logging
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from backend.core.config import settings

logger = logging.getLogger("finsight.security")

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Appends OWASP-recommended HTTP security headers to protect against
    MIME sniffing, clickjacking, cross-site scripting, and framing.
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "connect-src 'self' http://localhost:* http://127.0.0.1:*"
        )
        return response

class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """
    Attaches a unique Request Correlation ID (X-Request-ID) to every HTTP request
    for full end-to-end audit tracing and structured log correlation.
    """
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.perf_counter()
        
        response: Response = await call_next(request)
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"
        
        logger.info(
            f"{request.method} {request.url.path} completed with {response.status_code} "
            f"in {duration_ms:.2f}ms [req_id={request_id}]"
        )
        return response

class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    In-memory Sliding Window Rate Limiter per client IP address.
    Protects quantitative Monte Carlo and NLP vectorizers from Denial of Service (DoS).
    """
    def __init__(self, app, requests_per_minute: int = 180):
        super().__init__(app)
        self.rpm = requests_per_minute
        # Dict mapping IP to (request_count, window_start_time)
        self.clients: Dict[str, Tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next):
        # Exclude static/health routes from rate limits
        if request.url.path in ("/api/health", "/docs", "/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        count, start_time = self.clients.get(client_ip, (0, now))
        
        if now - start_time > 60:
            # Reset 60s window
            self.clients[client_ip] = (1, now)
        else:
            if count >= self.rpm:
                logger.warning(f"Rate limit exceeded for IP {client_ip} on {request.url.path}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded. Please throttle requests.",
                        "code": "RATE_LIMIT_EXCEEDED",
                        "retry_after_seconds": int(60 - (now - start_time))
                    },
                    headers={"Retry-After": str(int(60 - (now - start_time)))}
                )
            self.clients[client_ip] = (count + 1, start_time)

        return await call_next(request)

class RequestBodyLimitMiddleware(BaseHTTPMiddleware):
    """
    Rejects requests whose payload exceeds MAX_REQUEST_BODY_BYTES to prevent memory exhaustion DoS.
    """
    def __init__(self, app, max_bytes: int = settings.MAX_REQUEST_BODY_BYTES):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_bytes:
            logger.warning(f"Payload size {content_length} bytes exceeds allowed limit {self.max_bytes}")
            return JSONResponse(
                status_code=413,
                content={
                    "error": f"Request entity too large. Maximum allowed is {self.max_bytes // (1024*1024)}MB.",
                    "code": "PAYLOAD_TOO_LARGE"
                }
            )
        return await call_next(request)
