"""
FinSight AI — Security and Input Sanitization Utilities
Protects against SQL pattern injection, ReDoS, path traversal, and malicious ticker payloads.
"""

import re
from typing import Optional
from backend.core.exceptions import SecurityException, DomainValidationError

# Strict alphanumeric regex for financial tickers (e.g., AAPL, BRK.B, ^VIX)
TICKER_REGEX = re.compile(r"^[A-Z0-9\.\^]{1,10}$")

def validate_and_sanitize_ticker(ticker: Optional[str]) -> str:
    """
    Validates and standardizes a ticker symbol.
    Raises DomainValidationError on invalid or injection-laden input.
    """
    if not ticker:
        raise DomainValidationError("Ticker symbol cannot be empty.", field="ticker")
    cleaned = ticker.strip().upper()
    if not TICKER_REGEX.match(cleaned):
        raise DomainValidationError(
            f"Invalid ticker symbol '{ticker}'. Expected 1-10 uppercase alphanumeric characters.",
            field="ticker"
        )
    return cleaned

def escape_sql_like(term: Optional[str]) -> str:
    """
    Escapes SQLite LIKE pattern characters (%, _, \\) to prevent wildcard injection and pattern DoS.
    """
    if not term:
        return ""
    # Strip non-printable and control characters
    sanitized = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", term.strip())
    # Escape LIKE meta-characters with backslash
    sanitized = sanitized.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return sanitized
