"""
FinSight AI — Base Repository
Provides foundational data access methods using SQLite context management and Row factories.
"""

import sqlite3
from typing import Generator, List, Dict, Any, Optional
from backend.database.db import get_connection, get_db_cursor
from backend.core.exceptions import DatabaseException

class BaseRepository:
    def __init__(self):
        pass

    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        return get_db_cursor()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns rows as dictionaries."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except sqlite3.Error as e:
            raise DatabaseException(f"Database query failed: {e}")

    def execute_scalar(self, query: str, params: tuple = ()) -> Any:
        """Executes a query and returns the first column of the first row."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except sqlite3.Error as e:
            raise DatabaseException(f"Database scalar query failed: {e}")
