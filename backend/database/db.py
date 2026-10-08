import sqlite3
import json
from typing import Dict, Any, List, Optional
from backend.config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    cursor = conn.cursor()

    # Events table
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

    # Portfolio Positions table
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

    # Rebalance History table
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

    # Stress Tests table
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

    # Stock OHLCV Historical / Realtime Cache table (inspired by stock-data-intelligence-dashboard)
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

    # Portfolio Value History table
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
    print("[OK] SQLite database initialized successfully.")

if __name__ == "__main__":
    init_db()
