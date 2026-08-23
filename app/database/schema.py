import sqlite3
from pathlib import Path

def initialize_schema(db_path: Path):
    """Deploy institutional-grade candle schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Candles table: Immutable source of truth
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candles (
            symbol TEXT,
            timeframe TEXT,
            timestamp INTEGER,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            tick_volume INTEGER,
            spread INTEGER,
            real_volume INTEGER,
            PRIMARY KEY (symbol, timeframe, timestamp)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"[DB] Relational schema verified at {db_path.name}")