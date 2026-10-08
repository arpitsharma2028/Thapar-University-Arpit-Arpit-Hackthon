import sqlite3
import logging
from contextlib import contextmanager
from typing import Generator
from backend.config import DB_PATH

logger = logging.getLogger("finsight.database")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db_cursor() -> Generator[sqlite3.Cursor, None, None]:
    """
    Context manager providing automatic transaction commit, rollback on exception,
    and guaranteed connection closure.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.error(f"Database transaction rolled back due to error: {exc}")
        raise
    finally:
        conn.close()

def init_db():
    conn = get_connection()
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    cursor = conn.cursor()

    # Risk Events Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE NOT NULL,
        headline TEXT NOT NULL,
        text TEXT NOT NULL,
        source_type TEXT NOT NULL,
        source TEXT NOT NULL,
        category TEXT NOT NULL,
        sentiment_score REAL NOT NULL,
        impact_score REAL NOT NULL,
        tickers TEXT NOT NULL,
        sector TEXT NOT NULL,
        confidence REAL NOT NULL,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        timestamp TEXT NOT NULL
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_category ON events(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")

    # Portfolio Positions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        sector TEXT NOT NULL,
        target_weight REAL NOT NULL,
        current_weight REAL NOT NULL,
        shares INTEGER NOT NULL,
        current_price REAL NOT NULL,
        position_value REAL NOT NULL,
        last_rebalanced TEXT NOT NULL
    )
    """)

    # Rebalance Audit Trail Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rebalance_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        trigger_event_id TEXT,
        trigger_headline TEXT,
        trigger_sentiment REAL,
        trigger_impact REAL,
        affected_tickers TEXT,
        old_weights TEXT NOT NULL,       -- JSON
        new_weights TEXT NOT NULL,       -- JSON
        weight_deltas TEXT NOT NULL,     -- JSON
        portfolio_value_before REAL,
        portfolio_value_after REAL,
        formula_applied TEXT
    )
    """)

    # Stress Test Scenarios Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stress_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id TEXT UNIQUE NOT NULL,
        timestamp TEXT NOT NULL,
        scenario_id TEXT NOT NULL,
        scenario_name TEXT NOT NULL,
        severity REAL NOT NULL,
        category TEXT NOT NULL,
        trigger_event_id TEXT,
        value_before REAL NOT NULL,
        value_after REAL NOT NULL,
        total_loss REAL NOT NULL,
        loss_pct REAL NOT NULL,
        asset_impacts TEXT NOT NULL,      -- JSON
        sector_shocks TEXT NOT NULL,      -- JSON
        worst_positions TEXT NOT NULL     -- JSON
    )
    """)

    # Historical and Real-Time OHLCV Market Data Cache Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_ohlcv (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        date TEXT NOT NULL,
        open REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        close REAL NOT NULL,
        volume INTEGER NOT NULL,
        daily_return REAL,
        ma7 REAL,
        data_source TEXT DEFAULT 'yfinance',
        UNIQUE(symbol, date)
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_ohlcv_sym_date ON stock_ohlcv(symbol, date)")

    # Mark-to-Market Valuation History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        total_value REAL NOT NULL,
        portfolio_sentiment REAL NOT NULL,
        risk_level TEXT NOT NULL,
        trigger_note TEXT
    )
    """)

    conn.commit()
    conn.close()
    logger.info("Database schema initialized and verified.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
