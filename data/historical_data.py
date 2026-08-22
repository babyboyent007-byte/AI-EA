import sqlite3
import MetaTrader5 as mt5
import pandas as pd
import numpy as np

from database import create_tables, get_connection


def download_symbol_candles(symbol: str, timeframe, timeframe_name: str, target_bars: int, conn: sqlite3.Connection):
    """Download historical candles for a symbol in chunks and store into SQLite database."""
    print(f"\n--- Downloading {symbol} ({timeframe_name}, target: {target_bars:,} bars) ---")
    
    if not mt5.symbol_select(symbol, True):
        print(f"Warning: Failed to select symbol {symbol} in Market Watch.")
        return 0

    chunk_size = 50000
    all_chunks = []
    fetched_total = 0

    for pos in range(0, target_bars, chunk_size):
        count = min(chunk_size, target_bars - pos)
        chunk = mt5.copy_rates_from_pos(symbol, timeframe, pos, count)
        if chunk is not None and len(chunk) > 0:
            all_chunks.append(chunk)
            fetched_total += len(chunk)
            if len(chunk) < count:
                # No more older history available from broker
                break
        else:
            break

    if not all_chunks:
        print(f"No rates returned for {symbol}.")
        return 0

    rates = np.concatenate(all_chunks[::-1])
    df = pd.DataFrame(rates)
    df.drop_duplicates(subset=['time'], inplace=True)
    df.sort_values(by='time', inplace=True)
    df.reset_index(drop=True, inplace=True)

    df["symbol"] = symbol
    df["timeframe"] = timeframe_name

    # Store into SQLite using INSERT OR REPLACE to prevent duplicate key errors
    records = df[[
        "symbol", "timeframe", "time", "open", "high", "low", "close",
        "tick_volume", "spread", "real_volume"
    ]].to_records(index=False).tolist()

    cursor = conn.cursor()
    cursor.executemany("""
        INSERT OR REPLACE INTO candles (
            symbol, timeframe, time, open, high, low, close,
            tick_volume, spread, real_volume
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)
    conn.commit()

    print(f"Successfully stored {len(records):,} candles for {symbol} ({timeframe_name}).")
    return len(records)


def main():
    # Initialize database tables
    create_tables()

    # Initialize MT5
    if not mt5.initialize():
        print("MT5 Initialization Failed")
        print(mt5.last_error())
        quit()

    targets = [
        ("EURUSD", mt5.TIMEFRAME_M5, "M5", 200000),
        ("GBPUSD", mt5.TIMEFRAME_M5, "M5", 200000),
        ("USDJPY", mt5.TIMEFRAME_M5, "M5", 200000),
        ("XAUUSD", mt5.TIMEFRAME_M5, "M5", 200000),
        ("BTCUSD", mt5.TIMEFRAME_M5, "M5", 100000),
    ]

    conn = get_connection()

    total_downloaded = 0
    try:
        for symbol, tf, tf_name, bars in targets:
            # Check symbol availability
            sym_info = mt5.symbol_info(symbol)
            if sym_info is None:
                # Check for common broker suffixes (e.g. BTCUSDm, BTCUSDi)
                all_symbols = [s.name for s in mt5.symbols_get() or []]
                matched = [s for s in all_symbols if s.startswith(symbol)]
                if matched:
                    symbol = matched[0]
                    print(f"Using matched broker symbol: {symbol}")
                else:
                    print(f"Symbol {symbol} is not available on this broker. Skipping.")
                    continue

            count = download_symbol_candles(symbol, tf, tf_name, bars, conn)
            total_downloaded += count
    finally:
        conn.close()
        mt5.shutdown()

    print(f"\nCompleted! Total candles stored across all symbols: {total_downloaded:,}")


if __name__ == "__main__":
    main()
