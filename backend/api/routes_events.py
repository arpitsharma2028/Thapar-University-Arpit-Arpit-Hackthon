from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
from backend.services.event_service import EventService
from backend.models.schemas import TextAnalysisRequest, RiskSignalResponse

router = APIRouter(prefix="/api/events", tags=["Risk Events"])
event_service = EventService()

@router.get("")
def list_events(
    source_type: Optional[str] = Query(None, description="Filter by News or Social"),
    category: Optional[str] = Query(None, description="Filter by event category"),
    min_impact: Optional[float] = Query(None, description="Minimum impact severity (1-10)"),
    min_sentiment: Optional[float] = Query(None, description="Minimum sentiment (-1.0 to 1.0)"),
    max_sentiment: Optional[float] = Query(None, description="Maximum sentiment (-1.0 to 1.0)"),
    search: Optional[str] = Query(None, description="Search term for headline, text, or tickers"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List historical and live risk signals with multi-dimensional filtering.
    """
    return event_service.get_events(
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
def analyze_custom_text(request: TextAnalysisRequest):
    """
    Executes the Unified NLP Risk Engine on raw text:
    Extracts sentiment, classifies category, scores impact, identifies entities & sector.
    """
    if not request.text or len(request.text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Input text must be at least 5 characters.")

    result = event_service.analyze_and_store(
        text=request.text,
        headline=request.headline,
        source=request.source or "User Manual Input",
        source_type=request.source_type or "News"
    )
    return result

@router.get("/next-sim")
def get_next_simulation_event():
    """
    Returns a sample event from the database to drive interactive demo simulations.
    """
    evt = event_service.get_next_simulation_event()
    if not evt:
        raise HTTPException(status_code=404, detail="No simulation events found in database.")
    return evt
