import sqlite3
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional

class RelationalRepository:
    """
    Release 0.2.0: SQL Data Access Object (DAO).
    Provides institutional-grade persistence for candles, features, and trade logs.
    """
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._initialize_schema()

    def _initialize_schema(self):
        """Ensures all core tables exist in the SQLite backend."""
        queries = [
            """CREATE TABLE IF NOT EXISTS candles (
                timestamp DATETIME, symbol TEXT, timeframe TEXT, 
                open REAL, high REAL, low REAL, close REAL, volume INTEGER,
                PRIMARY KEY (timestamp, symbol, timeframe))""",
            """CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                timestamp DATETIME, symbol TEXT, confidence REAL, action TEXT)""",
            """CREATE TABLE IF NOT EXISTS trade_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_time DATETIME, exit_time DATETIME, symbol TEXT,
                entry_price REAL, exit_price REAL, pnl REAL)"""
        ]
        with sqlite3.connect(self.db_path) as conn:
            for q in queries:
                conn.execute(q)
        print(f"[SQL] Relational schema verified at {self.db_path.name}")

    def save_market_data(self, df: pd.DataFrame):
        """Persists OHLCV data with conflict resolution."""
        if df.empty: return
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql('candles_temp', conn, if_exists='replace', index=False)
            conn.execute('INSERT OR IGNORE INTO candles SELECT * FROM candles_temp')
            conn.execute('DROP TABLE candles_temp')

    def get_historical_window(self, symbol: str, limit: int = 500) -> pd.DataFrame:
        """Retrieves the most recent N bars for feature calculation."""
        with sqlite3.connect(self.db_path) as conn:
            query = f"SELECT * FROM candles WHERE symbol = ? ORDER BY timestamp DESC LIMIT ?"
            return pd.read_sql(query, conn, params=(symbol, limit)).sort_values('timestamp')