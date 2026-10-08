"""
FinSight AI — Quantitative Market & Portfolio Risk Intelligence Engine
Main FastAPI application entrypoint with Clean Architecture, defense-in-depth security,
standardized exception handling, and rate limiting.
"""

import sys
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Ensure workspace root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("finsight.main")

from backend.core.config import settings
from backend.core.exceptions import FinSightException
from backend.core.middleware import (
    SecurityHeadersMiddleware,
    RequestCorrelationMiddleware,
    RateLimiterMiddleware,
    RequestBodyLimitMiddleware
)
from backend.database.db import init_db
from backend.ml.nlp_engine import get_risk_engine
from backend.api import (
    events_router,
    portfolio_router,
    stress_router,
    metrics_router,
    market_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing FinSight AI Market & Portfolio Risk Intelligence Engine...")
    init_db()
    get_risk_engine()
    logger.info("Core engine services and statistical models operational.")
    yield
    logger.info("Shutting down FinSight AI Engine...")

app = FastAPI(
    title=settings.SERVICE_NAME,
    description=(
        "Institutional platform for high-frequency unstructured financial text processing, "
        "tactical index dynamic rebalancing (Module A), wholesale multi-asset portfolio stress testing (Module B), "
        "and stochastic Monte Carlo price forecasting."
    ),
    version=settings.VERSION,
    lifespan=lifespan
)

# 1. Defense-in-Depth Middleware Stack (Outer to Inner)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestCorrelationMiddleware)
app.add_middleware(RateLimiterMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)
app.add_middleware(RequestBodyLimitMiddleware, max_bytes=settings.MAX_REQUEST_BODY_BYTES)

# 2. Strict CORS Configuration: Explicitly Whitelisted Origins (OWASP Compliance)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time-Ms"]
)

# 3. Global Exception Handlers (Prevent Information Leakage & Provide RFC 7807 Details)
@app.exception_handler(FinSightException)
async def domain_exception_handler(request: Request, exc: FinSightException):
    request_id = getattr(request.state, "request_id", None)
    logger.warning(f"Domain error on {request.url.path} [{exc.code}]: {exc.message} [req_id={request_id}]")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "code": exc.code,
            "status": exc.status_code,
            "request_id": request_id,
            "details": exc.details
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", None)
    logger.warning(f"Validation failure on {request.url.path}: {exc.errors()} [req_id={request_id}]")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Request validation failed",
            "code": "VALIDATION_ERROR",
            "status": 422,
            "request_id": request_id,
            "details": {"validation_errors": exc.errors()}
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": "HTTP_ERROR",
            "status": exc.status_code,
            "request_id": request_id
        }
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    logger.error(f"Unhandled system error on {request.url.path}: {exc} [req_id={request_id}]", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "An internal error occurred. Please contact system support.",
            "code": "INTERNAL_SERVER_ERROR",
            "status": 500,
            "request_id": request_id
        }
    )

# 4. Route Registration
app.include_router(events_router)
app.include_router(portfolio_router)
app.include_router(stress_router)
app.include_router(metrics_router)
app.include_router(market_router)

@app.get("/")
def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "documentation": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
