"""
FinSight AI — Database Seeder Script
Initializes SQLite database schema and seeds it with:
- Initial portfolio positions from data/portfolio.csv
- Baseline news and social events from data/news_events.csv and data/social_events.csv
- Baseline portfolio history point
"""

import os
import sys
import pandas as pd
import sqlite3
from datetime import datetime

# UTF-8 stdout configuration
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "backend", "database", "finsight.db")

from backend.database.db import init_db, get_connection

def seed_database():
    print("Initializing FinSight AI Database...")
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # Clear existing data for a fresh deterministic seed
    cursor.execute("DELETE FROM events")
    cursor.execute("DELETE FROM portfolio_positions")
    cursor.execute("DELETE FROM rebalance_history")
    cursor.execute("DELETE FROM stress_tests")
    cursor.execute("DELETE FROM portfolio_history")
    conn.commit()

    # 1. Seed Portfolio Positions
    portfolio_csv = os.path.join(DATA_DIR, "portfolio.csv")
    if os.path.exists(portfolio_csv):
        pdf = pd.read_csv(portfolio_csv)
        for _, row in pdf.iterrows():
            cursor.execute("""
            INSERT INTO portfolio_positions (
                ticker, name, sector, target_weight, current_weight, shares, current_price, position_value, last_rebalanced
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['ticker'], row['name'], row['sector'],
                float(row['target_weight']), float(row['current_weight']),
                int(row['shares']), float(row['current_price']),
                float(row['position_value']), str(row['last_rebalanced'])
            ))
        print(f"[OK] Seeded {len(pdf)} portfolio positions into portfolio_positions table.")

    # 2. Seed News & Social Events
    news_csv = os.path.join(DATA_DIR, "news_events.csv")
    social_csv = os.path.join(DATA_DIR, "social_events.csv")
    event_count = 0

    for path, stype in [(news_csv, "News"), (social_csv, "Social")]:
        if os.path.exists(path):
            edf = pd.read_csv(path)
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
                event_count += 1
    print(f"[OK] Seeded {event_count} events into events table.")

    # 3. Seed Baseline Portfolio History
    cursor.execute("SELECT SUM(position_value) FROM portfolio_positions")
    total_val = cursor.fetchone()[0] or 10_000_000.0
    cursor.execute("""
    INSERT INTO portfolio_history (timestamp, total_value, portfolio_sentiment, risk_level, trigger_note)
    VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        round(total_val, 2),
        0.05,
        "Moderate",
        "Initial Portfolio Baseline"
    ))

    conn.commit()
    conn.close()
    print("[OK] Database seeded successfully.")

if __name__ == "__main__":
    seed_database()
