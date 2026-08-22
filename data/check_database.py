import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "market_data.db"
if not DB_PATH.exists() and Path("market_data.db").exists():
    DB_PATH = Path("market_data.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Check all tables in database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
print(f"Tables in {DB_PATH.name}:")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  - {table}: {count:,} rows")

# 2. Count candles total
cursor.execute("SELECT COUNT(*) FROM candles")
total_candles = cursor.fetchone()
print(f"\nTotal candles: {total_candles}")

# 3. Breakdown per symbol
cursor.execute("""
SELECT symbol, timeframe, COUNT(*), datetime(MIN(time), 'unixepoch'), datetime(MAX(time), 'unixepoch')
FROM candles
GROUP BY symbol, timeframe
""")
print("\nCandles per Symbol / Timeframe:")
for row in cursor.fetchall():
    print(f"  {row[0]} ({row[1]}): {row[2]:,} bars | Range: {row[3]} to {row[4]}")

# 4. Preview sample rows
cursor.execute("""
SELECT *
FROM candles
LIMIT 5
""")

print("\nSample Rows:")
for row in cursor.fetchall():
    print(row)

conn.close()
