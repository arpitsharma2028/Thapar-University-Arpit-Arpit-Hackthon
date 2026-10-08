"""
FinSight AI — Stress Test Repository (Data Access Layer)
Encapsulates database access for wholesale banking portfolio stress tests and scenario logs.
"""

import json
from typing import List, Dict, Any
from backend.repositories.base import BaseRepository

class StressRepository(BaseRepository):
    def insert_stress_test(self, record: Dict[str, Any]) -> str:
        with self.get_cursor() as cursor:
            cursor.execute("""
            INSERT INTO stress_tests (
                test_id, timestamp, scenario_id, scenario_name, severity, category,
                trigger_event_id, value_before, value_after, total_loss, loss_pct,
                asset_impacts, sector_shocks, worst_positions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record["test_id"],
                record["timestamp"],
                record["scenario_id"],
                record["scenario_name"],
                float(record["severity"]),
                record["category"],
                record.get("trigger_event_id"),
                float(record["value_before"]),
                float(record["value_after"]),
                float(record["total_loss"]),
                float(record["loss_pct"]),
                json.dumps(record["asset_impacts"]),
                json.dumps(record["sector_shocks"]),
                json.dumps(record["worst_positions"])
            ))
        return record["test_id"]

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        rows = self.execute_query("SELECT * FROM stress_tests ORDER BY id DESC LIMIT ?", (limit,))
        for r in rows:
            for json_field in ("asset_impacts", "sector_shocks", "worst_positions"):
                if r.get(json_field) and isinstance(r[json_field], str):
                    try:
                        r[json_field] = json.loads(r[json_field])
                    except Exception:
                        pass
        return rows
