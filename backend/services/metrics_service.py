from typing import Dict, Any, List
from backend.database.db import get_connection

class MetricsService:
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()

        # Portfolio metrics
        cursor.execute("SELECT SUM(position_value) FROM portfolio_positions")
        total_val = cursor.fetchone()[0] or 10_000_000.0

        # Number of events
        cursor.execute("SELECT COUNT(*) FROM events")
        total_events = cursor.fetchone()[0]

        # Average sentiment
        cursor.execute("SELECT AVG(sentiment_score) FROM events")
        avg_sentiment = cursor.fetchone()[0] or 0.0

        # High impact alerts (impact >= 7.0)
        cursor.execute("SELECT COUNT(*) FROM events WHERE impact_score >= 7.0")
        high_impact_alerts = cursor.fetchone()[0]

        # Rebalance counts
        cursor.execute("SELECT COUNT(*) FROM rebalance_history")
        total_rebalances = cursor.fetchone()[0]

        # Stress tests performed
        cursor.execute("SELECT COUNT(*) FROM stress_tests")
        total_stress_tests = cursor.fetchone()[0]

        # Category distribution
        cursor.execute("SELECT category, COUNT(*) as count FROM events GROUP BY category ORDER BY count DESC")
        category_dist = [{"category": r[0], "count": r[1]} for r in cursor.fetchall()]

        # Sector allocations
        cursor.execute("SELECT sector, SUM(current_weight) as weight, SUM(position_value) as val FROM portfolio_positions GROUP BY sector ORDER BY weight DESC")
        sector_alloc = [{"sector": r[0], "weight": round(r[1], 4), "value": round(r[2], 2)} for r in cursor.fetchall()]

        # Portfolio value history
        cursor.execute("SELECT timestamp, total_value, portfolio_sentiment, risk_level FROM portfolio_history ORDER BY id ASC LIMIT 30")
        history_points = [dict(r) for r in cursor.fetchall()]

        # Recent live alerts
        cursor.execute("SELECT * FROM events ORDER BY id DESC LIMIT 5")
        recent_alerts = [dict(r) for r in cursor.fetchall()]

        conn.close()

        # Simulated Risk Metrics
        simulated_var_95 = round(total_val * 0.0245, 2)  # 1-day 95% Value at Risk
        simulated_sharpe = 1.84

        return {
            "portfolio": {
                "total_value": round(total_val, 2),
                "var_95_1day": simulated_var_95,
                "sharpe_ratio": simulated_sharpe,
                "total_rebalances": total_rebalances,
                "total_stress_tests": total_stress_tests
            },
            "risk_engine": {
                "total_events": total_events,
                "avg_sentiment": round(avg_sentiment, 3),
                "high_impact_alerts": high_impact_alerts,
                "category_distribution": category_dist
            },
            "sector_allocation": sector_alloc,
            "portfolio_history": history_points,
            "recent_alerts": recent_alerts
        }
