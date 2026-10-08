from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TextAnalysisRequest(BaseModel):
    text: str = Field(..., description="Financial news headline, article body, or social media post")
    headline: Optional[str] = Field(None, description="Optional headline")
    source: Optional[str] = Field("Manual Input", description="Source name")
    source_type: Optional[str] = Field("News", description="Source type: News or Social")

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
    event_id: Optional[str] = None
    headline: Optional[str] = None
    tickers: Optional[str] = None
    sector: Optional[str] = None
    sentiment_score: float
    impact_score: float
    sensitivity: Optional[float] = 0.025

class BatchSimulateRequest(BaseModel):
    num_events: int = Field(5, ge=1, le=25, description="Number of events to simulate in batch")
    sensitivity: Optional[float] = 0.025

class StressTestRequest(BaseModel):
    scenario_id: Optional[str] = None
    trigger_event_id: Optional[str] = None
    severity_multiplier: Optional[float] = Field(1.0, ge=0.1, le=3.0)
    custom_scenario: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    nlp_engine_loaded: bool
    database_connected: bool
    timestamp: str
