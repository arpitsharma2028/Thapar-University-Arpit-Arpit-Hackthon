import sys
import os
import tempfile
import sqlite3
import pytest
import pandas as pd
from datetime import datetime

# Add root directory to sys.path so 'backend' package is discoverable
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import backend.config
import backend.core.config
import backend.database.db

@pytest.fixture(scope="session", autouse=True)
def isolated_test_database():
    """
    Session-level autouse fixture:
    Creates an isolated temporary SQLite database for the test suite, initializes
    the schema, and seeds baseline test data so tests NEVER depend on manual seeding
    or an existing local database file.
    """
    temp_dir = tempfile.mkdtemp(prefix="finsight_test_")
    test_db_path = os.path.join(temp_dir, "test_finsight.db")

    # Patch database path across all modules
    original_db_path = backend.database.db.DB_PATH
    backend.database.db.DB_PATH = test_db_path
    backend.config.DB_PATH = test_db_path
    backend.core.config.DB_PATH = test_db_path
    backend.core.config.settings.DATABASE_PATH = test_db_path

    # Initialize schema
    backend.database.db.init_db()

    # Seed baseline portfolio positions from data/portfolio.csv
    data_dir = os.path.join(ROOT_DIR, "data")
    portfolio_csv = os.path.join(data_dir, "portfolio.csv")
    conn = backend.database.db.get_connection()
    cursor = conn.cursor()

    if os.path.exists(portfolio_csv):
        pdf = pd.read_csv(portfolio_csv)
        for _, row in pdf.iterrows():
            cursor.execute("""
            INSERT INTO portfolio_positions (
                ticker, name, sector, target_weight, current_weight, shares, current_price, position_value, last_rebalanced
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(row['ticker']), str(row['name']), str(row['sector']),
                float(row['target_weight']), float(row['current_weight']),
                int(row['shares']), float(row['current_price']),
                float(row['position_value']), str(row['last_rebalanced'])
            ))

    # Seed baseline events from data/news_events.csv
    news_csv = os.path.join(data_dir, "news_events.csv")
    if os.path.exists(news_csv):
        edf = pd.read_csv(news_csv).head(20)
        for _, row in edf.iterrows():
            cursor.execute("""
            INSERT OR IGNORE INTO events (
                event_id, headline, text, source_type, source, category,
                sentiment_score, impact_score, tickers, sector, confidence, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(row['event_id']), str(row['headline']), str(row['text']),
                str(row['source_type']), str(row['source']), str(row['category']),
                float(row['sentiment_score']), float(row['impact_score']),
                str(row['tickers']), str(row['sector']), float(row['confidence']),
                str(row['timestamp'])
            ))

    # Seed baseline portfolio history
    cursor.execute("""
    INSERT INTO portfolio_history (timestamp, total_value, portfolio_sentiment, risk_level, trigger_note)
    VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        10_000_000.0,
        0.05,
        "Moderate",
        "Test Baseline"
    ))

    # Seed deterministic OHLCV quotes with non-zero variance for tracked tickers to keep market tests offline
    sample_tickers = ["NVDA", "AAPL", "MSFT", "TSLA", "JPM"]
    today = datetime.now()
    import math
    for sym_idx, sym in enumerate(sample_tickers):
        base_p = 875.0 if sym == "NVDA" else (182.5 if sym == "AAPL" else 415.2)
        prev_p = base_p
        for d in range(30):
            dt_str = (today - pd.Timedelta(days=30 - d)).strftime("%Y-%m-%d")
            # Sine wave variation to guarantee positive variance & distinct returns
            cycle = math.sin((d + sym_idx * 3) / 4.0) * 0.02
            p = round(base_p * (1.0 + cycle + 0.001 * d), 2)
            ret = round(((p - prev_p) / prev_p) * 100, 4) if d > 0 else 0.5
            prev_p = p
            cursor.execute("""
            INSERT OR IGNORE INTO stock_ohlcv (symbol, date, open, high, low, close, volume, daily_return, ma7, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sym, dt_str, round(p * 0.995, 2), round(p * 1.015, 2), round(p * 0.985, 2),
                p, 5000000, ret, p, "synthetic_cache"
            ))

    conn.commit()
    conn.close()

    yield test_db_path

    # Teardown
    backend.database.db.DB_PATH = original_db_path
    backend.config.DB_PATH = original_db_path
    backend.core.config.DB_PATH = original_db_path
    backend.core.config.settings.DATABASE_PATH = original_db_path
    try:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass
