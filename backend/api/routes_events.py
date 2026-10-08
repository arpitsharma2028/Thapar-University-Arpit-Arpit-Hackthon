"""
FinSight AI — Risk Events API Router
Provides multi-dimensional event queries and NLP risk signal extraction with Dependency Injection.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Query, Depends, HTTPException
from backend.services.event_service import EventService
from backend.models.schemas import TextAnalysisRequest, RiskSignalResponse
from backend.api.deps import get_event_service
from backend.core.exceptions import EntityNotFoundException, DomainValidationError

router = APIRouter(prefix="/api/events", tags=["Risk Events"])

@router.get("", response_model=Dict[str, Any])
def list_events(
    source_type: Optional[str] = Query(None, max_length=20, description="Filter by News or Social"),
    category: Optional[str] = Query(None, max_length=50, description="Filter by event category"),
    min_impact: Optional[float] = Query(None, ge=1.0, le=10.0, description="Minimum impact severity (1-10)"),
    min_sentiment: Optional[float] = Query(None, ge=-1.0, le=1.0, description="Minimum sentiment (-1.0 to 1.0)"),
    max_sentiment: Optional[float] = Query(None, ge=-1.0, le=1.0, description="Maximum sentiment (-1.0 to 1.0)"),
    search: Optional[str] = Query(None, max_length=100, description="Search term for headline, text, or tickers"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: EventService = Depends(get_event_service)
):
    """
    List historical and live risk signals with multi-dimensional filtering.
    """
    return service.get_events(
        source_type=source_type,
        category=category,
        min_impact=min_impact,
        min_sentiment=min_sentiment,
        max_sentiment=max_sentiment,
        search=search,
        limit=limit,
        offset=offset
    )

@router.post("/analyze", response_model=RiskSignalResponse)
def analyze_custom_text(
    request: TextAnalysisRequest,
    service: EventService = Depends(get_event_service)
):
    """
    Executes the Unified NLP Risk Engine on raw text:
    Extracts sentiment, classifies category, scores impact, identifies entities & sector.
    """
    return service.analyze_and_store(
        text=request.text,
        headline=request.headline,
        source=request.source or "Manual Input",
        source_type=request.source_type or "News"
    )

@router.get("/next-sim")
def get_next_simulation_event(
    service: EventService = Depends(get_event_service)
):
    """
    Returns a sample event from the database to drive interactive demo simulations.
    """
    evt = service.get_next_simulation_event()
    if not evt:
        raise EntityNotFoundException("No simulation events found in registry.", entity_type="Event")
    return evt
