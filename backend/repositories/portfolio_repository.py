"""
FinSight AI — Portfolio Repository (Data Access Layer)
Encapsulates database access for portfolio positions, rebalance audit history, and valuation trajectory.
"""

import json
from typing import List, Dict, Any, Optional
from backend.repositories.base import BaseRepository

class PortfolioRepository(BaseRepository):
    def get_positions(self) -> List[Dict[str, Any]]:
        return self.execute_query("SELECT * FROM portfolio_positions ORDER BY current_weight DESC")

    def update_positions_and_log_rebalance(
        self,
        positions_to_update: List[Dict[str, Any]],
        rebalance_record: Dict[str, Any]
    ) -> None:
        """
        Executes atomic transaction updating all portfolio position weights and inserting
        an immutable regulatory audit log record in rebalance_history.
        """
        with self.get_cursor() as cursor:
            for p in positions_to_update:
                cursor.execute("""
                UPDATE portfolio_positions
                SET current_weight = ?, shares = ?, position_value = ?, last_rebalanced = ?
                WHERE ticker = ?
                """, (
                    p["current_weight"],
                    p["shares"],
                    p["position_value"],
                    p["last_rebalanced"],
                    p["ticker"]
                ))

            cursor.execute("""
            INSERT INTO rebalance_history (
                timestamp, trigger_event_id, trigger_headline, trigger_sentiment,
                trigger_impact, affected_tickers, old_weights, new_weights, weight_deltas,
                portfolio_value_before, portfolio_value_after, formula_applied
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rebalance_record["timestamp"],
                rebalance_record["trigger_event_id"],
                rebalance_record["trigger_headline"],
                rebalance_record["trigger_sentiment"],
                rebalance_record["trigger_impact"],
                rebalance_record["affected_tickers"],
                json.dumps(rebalance_record["old_weights"]),
                json.dumps(rebalance_record["new_weights"]),
                json.dumps(rebalance_record["weight_deltas"]),
                rebalance_record["portfolio_value_before"],
                rebalance_record["portfolio_value_after"],
                rebalance_record["formula_applied"]
            ))

    def reset_positions_to_target(self, timestamp: str, initial_portfolio_val: float) -> None:
        with self.get_cursor() as cursor:
            cursor.execute("""
            UPDATE portfolio_positions
            SET current_weight = target_weight,
                position_value = target_weight * ?,
                last_rebalanced = ?
            """, (initial_portfolio_val, timestamp))

    def get_rebalance_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        rows = self.execute_query("SELECT * FROM rebalance_history ORDER BY id DESC LIMIT ?", (limit,))
        for r in rows:
            for json_field in ("old_weights", "new_weights", "weight_deltas"):
                if r.get(json_field) and isinstance(r[json_field], str):
                    try:
                        r[json_field] = json.loads(r[json_field])
                    except Exception:
                        pass
        return rows

    def record_portfolio_valuation(
        self,
        timestamp: str,
        total_value: float,
        sentiment: float,
        risk_level: str,
        note: str = ""
    ) -> None:
        with self.get_cursor() as cursor:
            cursor.execute("""
            INSERT INTO portfolio_history (timestamp, total_value, portfolio_sentiment, risk_level, trigger_note)
            VALUES (?, ?, ?, ?, ?)
            """, (timestamp, total_value, sentiment, risk_level, note))
