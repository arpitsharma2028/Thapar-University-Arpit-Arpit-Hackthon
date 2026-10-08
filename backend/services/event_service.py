"""
FinSight AI — Event Service (Business Logic Layer)
Orchestrates NLP risk signal extraction, classification, and event persistence via EventRepository.
"""

import random
from typing import Dict, Any, List, Optional
from backend.repositories.event_repository import EventRepository
from backend.ml.nlp_engine import get_risk_engine, UnifiedRiskEngine

class EventService:
    def __init__(
        self,
        event_repo: Optional[EventRepository] = None,
        risk_engine: Optional[UnifiedRiskEngine] = None
    ):
        self.event_repo = event_repo or EventRepository()
        self.risk_engine = risk_engine or get_risk_engine()

    def get_events(
        self,
        source_type: Optional[str] = None,
        category: Optional[str] = None,
        min_impact: Optional[float] = None,
        min_sentiment: Optional[float] = None,
        max_sentiment: Optional[float] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        return self.event_repo.get_events(
            source_type=source_type,
            category=category,
            min_impact=min_impact,
            min_sentiment=min_sentiment,
            max_sentiment=max_sentiment,
            search=search,
            limit=limit,
            offset=offset
        )

    def analyze_and_store(
        self,
        text: str,
        headline: Optional[str] = None,
        source: str = "Live Feed",
        source_type: str = "News"
    ) -> Dict[str, Any]:
        """
        Analyzes raw unstructured text through the NLP Risk Engine and persists the structured signal.
        """
        signal = self.risk_engine.process_text(
            text=text,
            headline=headline,
            source=source,
            source_type=source_type
        )

        event_id = f"EVT-{random.randint(10000, 99999)}"
        signal["event_id"] = event_id

        self.event_repo.insert_event(signal)
        return signal

    def get_next_simulation_event(self) -> Optional[Dict[str, Any]]:
        return self.event_repo.get_random_simulation_event()
