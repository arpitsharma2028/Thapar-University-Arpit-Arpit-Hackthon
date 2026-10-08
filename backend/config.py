"""
FinSight AI — Configuration Bridge
Re-exports settings from backend.core.config for backward compatibility.
"""

from backend.core.config import (
    BASE_DIR,
    DATA_DIR,
    MODELS_DIR,
    DOCS_DIR,
    DB_PATH,
    Settings,
    settings,
    DEFAULT_SENSITIVITY,
    MIN_STOCK_WEIGHT,
    MAX_STOCK_WEIGHT,
    HIGH_IMPACT_THRESHOLD,
    INITIAL_PORTFOLIO_VALUE
)
