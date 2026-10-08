"""
FinSight AI — Rebalance Service (Module A: Business Logic Layer)
Implements tactical dynamic index rebalancing with bounded sensitivity and strict normalization.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.repositories.portfolio_repository import PortfolioRepository
from backend.repositories.event_repository import EventRepository
from backend.core.config import (
    DEFAULT_SENSITIVITY,
    MIN_STOCK_WEIGHT,
    MAX_STOCK_WEIGHT,
    INITIAL_PORTFOLIO_VALUE
)
from backend.core.exceptions import DomainValidationError, EntityNotFoundException

class RebalanceService:
    def __init__(
        self,
        portfolio_repo: Optional[PortfolioRepository] = None,
        event_repo: Optional[EventRepository] = None
    ):
        self.portfolio_repo = portfolio_repo or PortfolioRepository()
        self.event_repo = event_repo or EventRepository()
        self.min_weight = MIN_STOCK_WEIGHT
        self.max_weight = MAX_STOCK_WEIGHT
        self.sensitivity = DEFAULT_SENSITIVITY

    def get_current_portfolio(self) -> Dict[str, Any]:
        """
        Calculates aggregate portfolio valuation, asset-weighted sentiment, and risk posture.
        """
        positions = self.portfolio_repo.get_positions()
        if not positions:
            raise EntityNotFoundException("No active portfolio positions found.", entity_type="Portfolio")

        total_val = sum(p["position_value"] for p in positions)
        
        # Calculate asset-weighted sentiment from recent event signals
        recent_events = self.event_repo.get_events(limit=20)["events"]
        stock_sentiments: Dict[str, List[float]] = {}
        for ev in recent_events:
            tickers_raw = ev.get("tickers", "")
            ev_tickers = [t.strip() for t in tickers_raw.split(",") if t.strip()]
            for t in ev_tickers:
                stock_sentiments.setdefault(t, []).append(ev["sentiment_score"])

        avg_stock_sent = {
            t: round(sum(scores) / len(scores), 3) 
            for t, scores in stock_sentiments.items()
        }

        portfolio_sentiment = 0.0
        for p in positions:
            p["sentiment"] = avg_stock_sent.get(p["ticker"], 0.0)
            portfolio_sentiment += p["current_weight"] * p["sentiment"]

        portfolio_sentiment = round(portfolio_sentiment, 3)
        risk_level = "Low" if abs(portfolio_sentiment) < 0.2 and total_val > 9_500_000 else ("High" if portfolio_sentiment < -0.3 else "Moderate")

        return {
            "total_value": round(total_val, 2),
            "portfolio_sentiment": portfolio_sentiment,
            "risk_level": risk_level,
            "positions_count": len(positions),
            "positions": positions
        }

    def rebalance(
        self,
        trigger_event: Dict[str, Any],
        sensitivity: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Dynamically adjusts portfolio weights based on incoming event risk signals.
        Enforces:
          1. raw_delta = lambda * sentiment * (impact / 10.0) * beta_spillover
          2. clamp(weight, min_weight, max_weight)
          3. strict normalization: sum(weights) == 1.0000
        """
        sens = sensitivity if sensitivity is not None else self.sensitivity
        if sens <= 0 or sens > 0.5:
            raise DomainValidationError("Rebalancing sensitivity must be between 0.001 and 0.500.", field="sensitivity")

        positions = self.portfolio_repo.get_positions()
        if not positions:
            raise EntityNotFoundException("No portfolio positions available to rebalance.", entity_type="Portfolio")

        # Parse tickers safely
        raw_tickers = trigger_event.get("tickers", "")
        if isinstance(raw_tickers, list):
            event_tickers = [str(t).strip().upper() for t in raw_tickers if str(t).strip()]
        elif isinstance(raw_tickers, str):
            event_tickers = [t.strip().upper() for t in raw_tickers.split(",") if t.strip()]
        else:
            event_tickers = []

        event_sector = trigger_event.get("sector", "")
        sentiment = float(trigger_event.get("sentiment_score", 0.0))
        impact = float(trigger_event.get("impact_score", 5.0))
        impact_factor = max(0.1, min(1.0, impact / 10.0))

        old_weights: Dict[str, float] = {}
        target_weights: Dict[str, float] = {}
        new_weights: Dict[str, float] = {}
        weight_deltas: Dict[str, float] = {}

        # 1. Calculate raw deltas
        for p in positions:
            ticker = p["ticker"]
            old_w = p["current_weight"]
            old_weights[ticker] = old_w
            target_weights[ticker] = p["target_weight"]

            # Direct match vs Sector spillover
            if ticker in event_tickers:
                multiplier = 1.0
            elif p["sector"] == event_sector:
                multiplier = 0.45
            else:
                multiplier = 0.0

            raw_delta = sens * sentiment * impact_factor * multiplier
            new_weights[ticker] = old_w + raw_delta

        # 2. Strict Bounded Normalization (Simplex projection onto [min_weight, max_weight] with sum == 1.0)
        tickers = list(new_weights.keys())
        w = {t: max(self.min_weight, min(self.max_weight, new_weights[t])) for t in tickers}
        for _ in range(15):
            total = sum(w.values())
            if abs(total - 1.0) < 1e-6:
                break
            diff = 1.0 - total
            adjustable = [t for t in tickers if (diff > 0 and w[t] < self.max_weight) or (diff < 0 and w[t] > self.min_weight)]
            if not adjustable:
                break
            alloc = diff / len(adjustable)
            for t in adjustable:
                w[t] = max(self.min_weight, min(self.max_weight, w[t] + alloc))

        # Clean 4-decimal precision while guaranteeing sum == 1.0000
        new_weights = {t: round(val, 4) for t, val in w.items()}
        residual = round(1.0 - sum(new_weights.values()), 4)
        if residual != 0.0:
            candidates = [t for t in tickers if self.min_weight <= round(new_weights[t] + residual, 4) <= self.max_weight]
            target = candidates[0] if candidates else max(new_weights, key=new_weights.get)
            new_weights[target] = round(new_weights[target] + residual, 4)

        for ticker in new_weights:
            weight_deltas[ticker] = round(new_weights[ticker] - old_weights[ticker], 4)

        # 3. Mark to Market Valuation
        total_val_before = sum(p["position_value"] for p in positions)
        sentiment_shock = sentiment * impact_factor * 0.035
        total_val_after = round(total_val_before * (1.0 + sentiment_shock), 2)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 4. Prepare updated positions with all required schemas
        updated_positions = []
        for p in positions:
            ticker = p["ticker"]
            old_w = old_weights[ticker]
            new_w = new_weights[ticker]
            delta = weight_deltas[ticker]
            pos_val = round(total_val_after * new_w, 2)
            shares = int(pos_val / p["current_price"]) if p.get("current_price", 0) > 0 else p.get("shares", 0)
            updated_positions.append({
                "ticker": ticker,
                "company_name": p.get("company_name", ""),
                "sector": p.get("sector", ""),
                "old_weight": old_w,
                "new_weight": new_w,
                "current_weight": new_w,
                "weight_delta": delta,
                "shares": shares,
                "current_price": p.get("current_price", 0.0),
                "position_value": pos_val,
                "last_rebalanced": now_str
            })

        # 5. Persist atomically
        rebalance_record = {
            "timestamp": now_str,
            "trigger_event_id": trigger_event.get("event_id"),
            "trigger_headline": trigger_event.get("headline", ""),
            "trigger_sentiment": sentiment,
            "trigger_impact": impact,
            "affected_tickers": ",".join(event_tickers) if event_tickers else "Broad Market",
            "old_weights": old_weights,
            "new_weights": new_weights,
            "weight_deltas": weight_deltas,
            "portfolio_value_before": round(total_val_before, 2),
            "portfolio_value_after": total_val_after,
            "formula_applied": f"Bounded sensitivity delta with {self.min_weight*100}% floor and {self.max_weight*100}% ceiling"
        }

        self.portfolio_repo.update_positions_and_log_rebalance(updated_positions, rebalance_record)
        self.portfolio_repo.record_portfolio_valuation(
            timestamp=now_str,
            total_value=total_val_after,
            sentiment=sentiment,
            risk_level="High" if sentiment < -0.4 else "Moderate",
            note=f"Rebalance by {trigger_event.get('event_id', 'Event')}"
        )

        return {
            "status": "success",
            "trigger_event": trigger_event,
            "portfolio_value_before": round(total_val_before, 2),
            "portfolio_value_after": total_val_after,
            "value_change": round(total_val_after - total_val_before, 2),
            "weights_before": old_weights,
            "weights_after": new_weights,
            "deltas": weight_deltas,
            "updated_positions": updated_positions,
            "formula_applied": rebalance_record["formula_applied"]
        }

    def reset_portfolio(self) -> Dict[str, Any]:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.portfolio_repo.reset_positions_to_target(now_str, INITIAL_PORTFOLIO_VALUE)
        self.portfolio_repo.record_portfolio_valuation(
            timestamp=now_str,
            total_value=INITIAL_PORTFOLIO_VALUE,
            sentiment=0.05,
            risk_level="Moderate",
            note="Manual Portfolio Reset"
        )
        return {
            "status": "success",
            "message": "Portfolio weights reset to baseline target weights.",
            "total_value": INITIAL_PORTFOLIO_VALUE
        }

    def get_history(self, limit: int = 50) -> Dict[str, Any]:
        records = self.portfolio_repo.get_rebalance_history(limit=limit)
        return {
            "total": len(records),
            "history": records
        }
