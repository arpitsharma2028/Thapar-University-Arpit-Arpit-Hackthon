import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.database.db import get_connection
from backend.config import DEFAULT_SENSITIVITY, MIN_STOCK_WEIGHT, MAX_STOCK_WEIGHT

class RebalanceService:
    def __init__(self):
        self.min_weight = MIN_STOCK_WEIGHT
        self.max_weight = MAX_STOCK_WEIGHT
        self.sensitivity = DEFAULT_SENSITIVITY

    def get_current_portfolio(self) -> Dict[str, Any]:
        """
        Fetches current portfolio positions, weights, and total value.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM portfolio_positions ORDER BY current_weight DESC")
        rows = cursor.fetchall()

        positions = [dict(r) for r in rows]
        total_val = sum(p['position_value'] for p in positions)
        
        # Calculate weighted portfolio sentiment from recent event signals
        cursor.execute("""
            SELECT tickers, sentiment_score, impact_score 
            FROM events 
            ORDER BY id DESC LIMIT 20
        """)
        recent_events = cursor.fetchall()
        
        stock_sentiments = {}
        for ev in recent_events:
            ev_tickers = [t.strip() for t in ev['tickers'].split(',') if t.strip()]
            for t in ev_tickers:
                if t not in stock_sentiments:
                    stock_sentiments[t] = []
                stock_sentiments[t].append(ev['sentiment_score'])

        avg_stock_sent = {
            t: round(sum(scores)/len(scores), 3) 
            for t, scores in stock_sentiments.items()
        }

        portfolio_sentiment = 0.0
        for p in positions:
            p['sentiment'] = avg_stock_sent.get(p['ticker'], 0.0)
            portfolio_sentiment += p['current_weight'] * p['sentiment']

        portfolio_sentiment = round(portfolio_sentiment, 3)
        risk_level = "Low" if abs(portfolio_sentiment) < 0.2 and total_val > 9_500_000 else ("High" if portfolio_sentiment < -0.3 else "Moderate")

        conn.close()

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
        Formula:
          raw_delta = sensitivity * sentiment_score * (impact_score / 10.0)
          new_weight = old_weight + raw_delta
          clamp to [min_weight, max_weight]
          normalize: sum(new_weights) = 1.00
        """
        sens = sensitivity if sensitivity is not None else self.sensitivity
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM portfolio_positions")
        rows = cursor.fetchall()
        positions = [dict(r) for r in rows]

        if not positions:
            conn.close()
            raise ValueError("No portfolio positions found.")

        # Extract event attributes safely whether list or string
        raw_tickers = trigger_event.get("tickers", "")
        if isinstance(raw_tickers, list):
            event_tickers = [str(t).strip() for t in raw_tickers if str(t).strip()]
        elif isinstance(raw_tickers, str):
            event_tickers = [t.strip() for t in raw_tickers.split(",") if t.strip()]
        else:
            event_tickers = []
        event_sector = trigger_event.get("sector", "")
        sentiment = float(trigger_event.get("sentiment_score", 0.0))
        impact = float(trigger_event.get("impact_score", 5.0))
        impact_factor = max(0.1, min(1.0, impact / 10.0))

        old_weights = {p['ticker']: float(p['current_weight']) for p in positions}
        total_val_before = sum(p['position_value'] for p in positions)
        
        # Calculate raw deltas
        deltas = {}
        for p in positions:
            t = p['ticker']
            sec = p['sector']
            
            # Stock-specific impact vs Sector-wide impact
            if t in event_tickers:
                delta = sens * sentiment * impact_factor
            elif sec == event_sector and event_sector != "Broad Market":
                delta = sens * sentiment * impact_factor * 0.45  # Indirect sector spillover
            else:
                delta = 0.0
            deltas[t] = delta

        # Apply raw delta and enforce minimum non-negative floor
        tentative_weights = {}
        for t, old_w in old_weights.items():
            tentative_w = old_w + deltas[t]
            clamped_w = max(self.min_weight, min(self.max_weight, tentative_w))
            tentative_weights[t] = clamped_w

        # Normalization Step: Ensure strictly sum == 1.0000
        weight_sum = sum(tentative_weights.values())
        normalized_weights = {
            t: round(w / weight_sum, 4) 
            for t, w in tentative_weights.items()
        }

        # Fine-tune rounding difference to guarantee exact sum 1.0
        diff = 1.0 - sum(normalized_weights.values())
        if diff != 0:
            first_ticker = list(normalized_weights.keys())[0]
            normalized_weights[first_ticker] = round(normalized_weights[first_ticker] + diff, 4)

        # Calculate simulated price movements based on event
        # Event moves stock price proportionally: return = sentiment * impact_factor * beta * 2.5%
        updated_positions = []
        total_val_after = 0.0

        for p in positions:
            t = p['ticker']
            new_w = normalized_weights[t]
            old_w = old_weights[t]
            w_delta = round(new_w - old_w, 4)

            # Price movement
            price = p['current_price']
            if t in event_tickers:
                price_pct = sentiment * impact_factor * 0.035
            elif p['sector'] == event_sector:
                price_pct = sentiment * impact_factor * 0.015
            else:
                price_pct = (sentiment * 0.003) # minor broad market drift
            
            new_price = round(max(1.0, price * (1.0 + price_pct)), 2)

            updated_positions.append({
                "ticker": t,
                "name": p['name'],
                "sector": p['sector'],
                "old_weight": old_w,
                "new_weight": new_w,
                "weight_delta": w_delta,
                "old_price": price,
                "new_price": new_price
            })

        # Calculate updated position values based on new weights and portfolio valuation
        # Simulated value fluctuation:
        market_shock = 0.0
        for p in positions:
            t = p['ticker']
            if t in event_tickers:
                market_shock += old_weights[t] * (sentiment * impact_factor * 0.035)
            elif p['sector'] == event_sector:
                market_shock += old_weights[t] * (sentiment * impact_factor * 0.015)
        
        total_val_after = round(total_val_before * (1.0 + market_shock), 2)
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update Database positions
        for up in updated_positions:
            t = up['ticker']
            pos_val = round(total_val_after * up['new_weight'], 2)
            shares = round(pos_val / up['new_price'])
            up['position_value'] = pos_val
            up['shares'] = shares

            cursor.execute("""
            UPDATE portfolio_positions
            SET current_weight = ?, shares = ?, current_price = ?, position_value = ?, last_rebalanced = ?
            WHERE ticker = ?
            """, (up['new_weight'], shares, up['new_price'], pos_val, now_str, t))

        # Log to rebalance_history table
        weight_deltas_dict = {up['ticker']: up['weight_delta'] for up in updated_positions}
        cursor.execute("""
        INSERT INTO rebalance_history (
            timestamp, trigger_event_id, trigger_headline, trigger_sentiment, trigger_impact,
            affected_tickers, old_weights, new_weights, weight_deltas,
            portfolio_value_before, portfolio_value_after, formula_applied
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_str,
            trigger_event.get("event_id", "MANUAL-SIM"),
            trigger_event.get("headline", "Dynamic Rebalance Simulation"),
            sentiment,
            impact,
            ",".join(event_tickers),
            json.dumps(old_weights),
            json.dumps(normalized_weights),
            json.dumps(weight_deltas_dict),
            total_val_before,
            total_val_after,
            f"new_w = clamp(old_w + {sens} * {sentiment:.2f} * {impact_factor:.2f}, {self.min_weight}, {self.max_weight}); norm(sum=1.0)"
        ))

        # Log to portfolio_history table
        cursor.execute("""
        INSERT INTO portfolio_history (timestamp, total_value, portfolio_sentiment, risk_level, trigger_note)
        VALUES (?, ?, ?, ?, ?)
        """, (
            now_str,
            total_val_after,
            sentiment,
            "High" if impact >= 7.0 else "Normal",
            f"Rebalanced on {trigger_event.get('event_id', 'SIM')}"
        ))

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "timestamp": now_str,
            "trigger_event": trigger_event,
            "portfolio_value_before": round(total_val_before, 2),
            "portfolio_value_after": round(total_val_after, 2),
            "value_change": round(total_val_after - total_val_before, 2),
            "value_change_pct": round(((total_val_after - total_val_before) / total_val_before) * 100, 2),
            "updated_positions": updated_positions,
            "formula_applied": f"new_w = clamp(old_w + {sens} * sentiment * (impact/10), min={self.min_weight}, max={self.max_weight}); normalize()"
        }

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves rebalance history records.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rebalance_history ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            item = dict(r)
            item['old_weights'] = json.loads(item['old_weights'])
            item['new_weights'] = json.loads(item['new_weights'])
            item['weight_deltas'] = json.loads(item['weight_deltas'])
            result.append(item)
        conn.close()
        return result

    def reset_portfolio(self) -> Dict[str, Any]:
        """
        Resets portfolio to baseline target weights from companies.csv.
        """
        import os
        import pandas as pd
        from backend.config import DATA_DIR
        
        conn = get_connection()
        cursor = conn.cursor()
        
        pdf = pd.read_csv(os.path.join(DATA_DIR, "portfolio.csv"))
        for _, row in pdf.iterrows():
            cursor.execute("""
            UPDATE portfolio_positions
            SET current_weight = ?, shares = ?, current_price = ?, position_value = ?, last_rebalanced = ?
            WHERE ticker = ?
            """, (
                float(row['target_weight']), int(row['shares']), float(row['current_price']),
                float(row['position_value']), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                row['ticker']
            ))
            
        cursor.execute("DELETE FROM rebalance_history")
        cursor.execute("DELETE FROM portfolio_history")
        
        # Insert initial baseline
        cursor.execute("""
        INSERT INTO portfolio_history (timestamp, total_value, portfolio_sentiment, risk_level, trigger_note)
        VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            10_000_000.0,
            0.05,
            "Moderate",
            "Portfolio Reset to Baseline"
        ))

        conn.commit()
        conn.close()
        return {"status": "success", "message": "Portfolio reset to initial baseline weights."}
