import random
from typing import Dict, Any, List, Optional
from backend.database.db import get_connection
from backend.ml.nlp_engine import get_risk_engine

class EventService:
    def __init__(self):
        self.risk_engine = get_risk_engine()

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
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM events WHERE 1=1"
        params = []

        if source_type:
            query += " AND source_type = ?"
            params.append(source_type)
        if category:
            query += " AND category = ?"
            params.append(category)
        if min_impact is not None:
            query += " AND impact_score >= ?"
            params.append(min_impact)
        if min_sentiment is not None:
            query += " AND sentiment_score >= ?"
            params.append(min_sentiment)
        if max_sentiment is not None:
            query += " AND sentiment_score <= ?"
            params.append(max_sentiment)
        if search:
            query += " AND (headline LIKE ? OR text LIKE ? OR tickers LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term])

        # Get total matching count
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]

        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        events = [dict(r) for r in rows]

        conn.close()
        return {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "events": events
        }

    def analyze_and_store(
        self,
        text: str,
        headline: Optional[str] = None,
        source: str = "Live Feed",
        source_type: str = "News"
    ) -> Dict[str, Any]:
        """
        Analyzes custom text through the Unified NLP Risk Engine and stores it in SQLite.
        """
        signal = self.risk_engine.process_text(
            text=text,
            headline=headline,
            source=source,
            source_type=source_type
        )

        event_id = f"EVT-{random.randint(10000, 99999)}"
        signal["event_id"] = event_id

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO events (
            event_id, headline, text, source_type, source, category,
            sentiment_score, impact_score, tickers, sector, confidence, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            signal["headline"],
            signal["text"],
            signal["source_type"],
            signal["source"],
            signal["category"],
            signal["sentiment_score"],
            signal["impact_score"],
            ",".join(signal["tickers"]),
            signal["sector"],
            signal["confidence"],
            signal["timestamp"]
        ))
        conn.commit()
        conn.close()

        return signal

    def get_next_simulation_event(self) -> Dict[str, Any]:
        """
        Selects an event from the library for demo simulation.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
