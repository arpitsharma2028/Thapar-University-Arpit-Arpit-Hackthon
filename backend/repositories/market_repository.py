"""
FinSight AI — Market Repository (Data Access Layer)
Encapsulates database access for cached OHLCV market pricing, daily returns, and moving averages.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from backend.repositories.base import BaseRepository

class MarketRepository(BaseRepository):
    def count_records_for_symbol(self, symbol: str) -> int:
        return self.execute_scalar("SELECT COUNT(*) FROM stock_ohlcv WHERE symbol = ?", (symbol.upper(),)) or 0

    def save_ohlcv_dataframe(self, df: pd.DataFrame, symbol: str, data_source: str = "yfinance") -> int:
        records_saved = 0
        with self.get_cursor() as cursor:
            for _, row in df.iterrows():
                cursor.execute("""
                INSERT OR REPLACE INTO stock_ohlcv 
                (symbol, date, open, high, low, close, volume, daily_return, ma7, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol.upper(),
                    row["date"],
                    float(row["open"]),
                    float(row["high"]),
                    float(row["low"]),
                    float(row["close"]),
                    int(row["volume"]),
                    float(row["daily_return"]),
                    float(row["ma7"]),
                    data_source
                ))
                records_saved += 1
        return records_saved

    def get_ohlcv(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        query = """
        SELECT * FROM stock_ohlcv
        WHERE symbol = ? AND date >= ?
        ORDER BY date ASC
        """
        return self.execute_query(query, (symbol.upper(), cutoff))

    def get_latest_record(self, symbol: str) -> Optional[Dict[str, Any]]:
        rows = self.execute_query("""
        SELECT * FROM stock_ohlcv
        WHERE symbol = ?
        ORDER BY date DESC LIMIT 1
        """, (symbol.upper(),))
        return rows[0] if rows else None
