"""
FinSight AI — Event Repository (Data Access Layer)
Encapsulates all SQL persistence and querying for risk events, applying sanitized queries.
"""

from typing import List, Dict, Any, Optional
from backend.repositories.base import BaseRepository
from backend.core.security import escape_sql_like

class EventRepository(BaseRepository):
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
            escaped_term = f"%{escape_sql_like(search)}%"
            query += " AND (headline LIKE ? ESCAPE '\\' OR text LIKE ? ESCAPE '\\' OR tickers LIKE ? ESCAPE '\\')"
            params.extend([escaped_term, escaped_term, escaped_term])

        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        total_count = self.execute_scalar(count_query, tuple(params)) or 0

        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        events = self.execute_query(query, tuple(params))
        return {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "events": events
        }

    def insert_event(self, event_data: Dict[str, Any]) -> str:
        with self.get_cursor() as cursor:
            cursor.execute("""
            INSERT INTO events (
                event_id, headline, text, source_type, source, category,
                sentiment_score, impact_score, tickers, sector, confidence, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_data["event_id"],
                event_data["headline"],
                event_data["text"],
                event_data["source_type"],
                event_data["source"],
                event_data["category"],
                float(event_data["sentiment_score"]),
                float(event_data["impact_score"]),
                ",".join(event_data["tickers"]) if isinstance(event_data["tickers"], list) else str(event_data["tickers"]),
                event_data["sector"],
                float(event_data["confidence"]),
                event_data["timestamp"]
            ))
        return event_data["event_id"]

    def get_recent_events_for_ticker(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        escaped_ticker = f"%{escape_sql_like(ticker)}%"
        query = """
        SELECT sentiment_score, impact_score FROM events 
        WHERE tickers LIKE ? ESCAPE '\\'
        ORDER BY id DESC LIMIT ?
        """
        return self.execute_query(query, (escaped_ticker, limit))

    def get_random_simulation_event(self) -> Optional[Dict[str, Any]]:
        rows = self.execute_query("SELECT * FROM events ORDER BY RANDOM() LIMIT 1")
        return rows[0] if rows else None
