"""
FinSight AI — Domain Exception Hierarchy
Provides typed, structured exceptions for domain errors, preventing raw stack leakage.
"""

from typing import Optional, Dict, Any

class FinSightException(Exception):
    """Base exception for all FinSight domain errors."""
    def __init__(self, message: str, code: str = "FINSIGHT_ERROR", status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

class EntityNotFoundException(FinSightException):
    """Raised when a requested resource (event, stock, scenario) is not found."""
    def __init__(self, message: str, entity_type: str = "Resource", entity_id: Optional[str] = None):
        super().__init__(
            message=message,
            code="ENTITY_NOT_FOUND",
            status_code=404,
            details={"entity_type": entity_type, "entity_id": entity_id}
        )

class DomainValidationError(FinSightException):
    """Raised when business logic validation fails (e.g. invalid sensitivity, corrupted weights)."""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            code="DOMAIN_VALIDATION_ERROR",
            status_code=422,
            details={"field": field} if field else {}
        )

class RateLimitExceededException(FinSightException):
    """Raised when a client exceeds the allowable request rate."""
    def __init__(self, message: str = "Rate limit exceeded. Please retry later."):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429
        )

class SecurityException(FinSightException):
    """Raised on security violations (payload too large, invalid characters, CORS failure)."""
    def __init__(self, message: str, code: str = "SECURITY_VIOLATION"):
        super().__init__(
            message=message,
            code=code,
            status_code=403
        )

class DatabaseException(FinSightException):
    """Raised when persistence operations fail."""
    def __init__(self, message: str = "Database operation failed."):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500
        )
