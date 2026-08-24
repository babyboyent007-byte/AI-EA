import MetaTrader5 as mt5
import sqlite3
import pandas as pd
from datetime import datetime, timezone
import os

def get_last_bar_time(cursor, symbol, timeframe):
    cursor.execute("SELECT MAX(time) FROM bars WHERE symbol=? AND timeframe=?", (symbol, timeframe))
    result = cursor.fetchone()[0]
    return result

def sync_market_data(db_path):
    if not mt5.initialize():
        print(f"MT5 Init failed: {mt5.last_error()}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
    tf_map = {'M15': mt5.TIMEFRAME_M15, 'H1': mt5.TIMEFRAME_H1}

    for symbol in symbols:
        for tf_str, tf_const in tf_map.items():
            last_time_str = get_last_bar_time(cursor, symbol, tf_str)
            
            if last_time_str:
                start_dt = pd.to_datetime(last_time_str).to_pydatetime()
                print(f"[SYNC] {symbol} {tf_str} from {start_dt}")
            else:
                start_dt = datetime(2018, 1, 1, tzinfo=timezone.utc)
                print(f"[SYNC] {symbol} {tf_str} initial download (2018)")

            end_dt = datetime.now(timezone.utc)
            rates = mt5.copy_rates_range(symbol, tf_const, start_dt, end_dt)

            if rates is not None and len(rates) > 0:
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s').dt.strftime('%Y-%m-%d %H:%M:%S')
                
                bars_data = []
                for _, row in df.iterrows():
                    bars_data.append((symbol, tf_str, row['time'], row['open'], row['high'], row['low'], row['close'], row['tick_volume']))
                
                query = "INSERT OR IGNORE INTO bars (symbol, timeframe, time, open, high, low, close, tick_volume) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                cursor.executemany(query, bars_data)
                conn.commit()
                print(f"[OK] Synchronized {len(rates)} bars for {symbol} {tf_str}")
            else:
                print(f"[INFO] No new data for {symbol} {tf_str}")

    conn.close()
    mt5.shutdown()

if __name__ == '__main__':
    db_loc = os.path.join('database', 'market.db')
    sync_market_data(db_loc)