import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional

class CandleRepository:
    """Relational Data Access Object for Candles."""
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def save_candles(self, df: pd.DataFrame):
        """Persists candles with INSERT OR IGNORE logic."""
        if df.empty: return
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql('candles', conn, if_exists='append', index=False, method='multi')

    def get_latest_timestamp(self, symbol: str, timeframe: str) -> Optional[int]:
        """Retrieves highest timestamp to enable incremental downloads."""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT MAX(timestamp) FROM candles WHERE symbol = ? AND timeframe = ?"
            res = conn.execute(query, (symbol, timeframe)).fetchone()
            return res[0] if res else None