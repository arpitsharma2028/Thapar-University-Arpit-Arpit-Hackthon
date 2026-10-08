"""
FinSight AI — Centralized Application Configuration
Provides validated, immutable configuration settings with environment variable overrides.
"""

import os
from typing import List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "backend", "ml", "saved_models")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
DB_PATH = os.path.join(BASE_DIR, "backend", "database", "finsight.db")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

class Settings:
    # Environment & Service Metadata
    ENVIRONMENT: str = os.getenv("FINSIGHT_ENV", "production")
    SERVICE_NAME: str = "FinSight AI Quantitative Risk Intelligence Platform"
    VERSION: str = "1.1.0"
    DEBUG: bool = os.getenv("FINSIGHT_DEBUG", "false").lower() in ("true", "1", "yes")

    # Security & CORS: Explicit whitelisted origins (prevents arbitrary cross-origin requests)
    CORS_ALLOWED_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv(
            "FINSIGHT_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:8000"
        ).split(",") if origin.strip()
    ]

    # Rate Limiting & Resource Protection (DoS Defense)
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("FINSIGHT_RATE_LIMIT_RPM", "180"))
    MAX_REQUEST_BODY_BYTES: int = int(os.getenv("FINSIGHT_MAX_BODY_BYTES", str(2 * 1024 * 1024))) # 2MB limit

    # Database Settings
    DATABASE_PATH: str = DB_PATH
    DB_BUSY_TIMEOUT_MS: int = 30000
    DB_CONNECTION_TIMEOUT: float = 30.0

    # Quantitative Rebalancing Parameters (Module A)
    DEFAULT_SENSITIVITY: float = 0.025
    MIN_STOCK_WEIGHT: float = 0.010   # 1.0% floor
    MAX_STOCK_WEIGHT: float = 0.250   # 25.0% concentration cap
    HIGH_IMPACT_THRESHOLD: float = 7.0
    INITIAL_PORTFOLIO_VALUE: float = 10_000_000.0  # $10M baseline

settings = Settings()

# Module-level aliases for direct imports
DEFAULT_SENSITIVITY = settings.DEFAULT_SENSITIVITY
MIN_STOCK_WEIGHT = settings.MIN_STOCK_WEIGHT
MAX_STOCK_WEIGHT = settings.MAX_STOCK_WEIGHT
HIGH_IMPACT_THRESHOLD = settings.HIGH_IMPACT_THRESHOLD
INITIAL_PORTFOLIO_VALUE = settings.INITIAL_PORTFOLIO_VALUE
