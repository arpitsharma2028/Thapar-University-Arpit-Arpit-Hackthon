"""
FinSight AI — Domain Pydantic Schemas & Request/Response Contracts
Provides rigorous input validation, type safety, field bounds, and RFC 7807 error models.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

class TextAnalysisRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=5,
        max_length=10000,
        description="Financial news text, SEC filing excerpt, or social commentary (max 10,000 chars)"
    )
    headline: Optional[str] = Field(
        None,
        max_length=300,
        description="Optional headline summary"
    )
    source: Optional[str] = Field(
        "Manual Input",
        max_length=100,
        description="Originating source name (e.g., Bloomberg, Reuters, StockTwits)"
    )
    source_type: Optional[str] = Field(
        "News",
        pattern=r"^(News|Social)$",
        description="Source type classification ('News' or 'Social')"
    )

class RiskSignalResponse(BaseModel):
    headline: str
    text: str
    source_type: str
    source: str
    category: str
    sentiment_score: float
    impact_score: float
    tickers: List[str]
    companies: List[str]
    sector: str
    confidence: float
    timestamp: str
    event_id: Optional[str] = None

class RebalanceRequest(BaseModel):
    event_id: Optional[str] = Field(None, max_length=50)
    headline: Optional[str] = Field(None, max_length=300)
    tickers: Optional[str] = Field(None, max_length=200)
    sector: Optional[str] = Field(None, max_length=100)
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment polarity (-1.0 to +1.0)")
    impact_score: float = Field(..., ge=1.0, le=10.0, description="Predicted severity (1.0 to 10.0)")
    sensitivity: Optional[float] = Field(
        0.025,
        ge=0.001,
        le=0.500,
        description="Rebalancing sensitivity coefficient lambda"
    )

class BatchSimulateRequest(BaseModel):
    num_events: int = Field(5, ge=1, le=25, description="Number of events to simulate in batch (1-25)")
    sensitivity: Optional[float] = Field(0.025, ge=0.001, le=0.500)

class StressTestRequest(BaseModel):
    scenario_id: Optional[str] = Field(None, max_length=50)
    trigger_event_id: Optional[str] = Field(None, max_length=50)
    severity_multiplier: Optional[float] = Field(1.0, ge=0.1, le=3.0)
    custom_scenario: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    nlp_engine_loaded: bool
    database_connected: bool
    timestamp: str

class ProblemDetailsResponse(BaseModel):
    """Standardized RFC 7807 problem details error model."""
    error: str
    code: str
    status: int
    request_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
