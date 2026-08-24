import os
import sqlite3
from datetime import datetime, timezone
import MetaTrader5 as mt5
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def initialize_mt5():
    """Step 1: Initialize MT5"""
    print("=== Step 1: Initializing MT5 ===")
    if not mt5.initialize():
        error = mt5.last_error()
        raise RuntimeError(f"MT5 initialization failed: {error}")
    print("MT5 initialized successfully.")


def login_mt5():
    """Step 2: Verify Login / Log in to MT5"""
    print("\n=== Step 2: Logging in / Verifying Account ===")
    account_info = mt5.account_info()
    if account_info is None:
        error = mt5.last_error()
        raise RuntimeError(f"Failed to get account info / login: {error}")
    
    print(f"Logged in successfully:")
    print(f"  Account Login: {account_info.login}")
    print(f"  Server:        {account_info.server}")
    print(f"  Company:       {account_info.company}")
    print(f"  Currency:      {account_info.currency}")
    print(f"  Balance:       {account_info.balance:.2f} {account_info.currency}")
    return account_info


def download_eurusd_data(start_year: int = 2018) -> pd.DataFrame:
    """Step 3: Download EURUSD historical data (2018 to today)"""
    symbol = "EURUSD"
    print(f"\n=== Step 3: Downloading {symbol} data ({start_year} - today) ===")
    
    # Ensure symbol is selected in Market Watch
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"Failed to select symbol {symbol}: {mt5.last_error()}")
    
    utc_from = datetime(start_year, 1, 1, tzinfo=timezone.utc)
    utc_to = datetime.now(timezone.utc)
    
    # Request daily candle rates
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_D1, utc_from, utc_to)
    
    if rates is None or len(rates) == 0:
        # Fallback to copy_rates_from_pos if range request needs cache warm-up
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 3000)
        if rates is None or len(rates) == 0:
            raise RuntimeError(f"Failed to copy rates for {symbol}: {mt5.last_error()}")
    
    # Create DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Filter to requested start date
    df = df[df['time'] >= pd.Timestamp(utc_from.date())].copy()
    df.reset_index(drop=True, inplace=True)
    
    print(f"Downloaded {len(df)} daily candles.")
    print(f"  Date range: {df['time'].min().strftime('%Y-%m-%d')} to {df['time'].max().strftime('%Y-%m-%d')}")
    print(f"  Columns: {list(df.columns)}")
    return df


def save_to_database(df: pd.DataFrame, db_path: str = "market_data.db", table_name: str = "eurusd_daily"):
    """Step 4: Save downloaded data to SQLite database"""
    print(f"\n=== Step 4: Saving data to database ({db_path} -> table '{table_name}') ===")
    conn = sqlite3.connect(db_path)
    
    # Ensure datetime is formatted nicely as string for SQLite compatibility
    save_df = df.copy()
    save_df['time'] = save_df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    save_df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    print(f"Saved {len(save_df)} rows to table '{table_name}' in SQLite database '{db_path}'.")


def read_from_database(db_path: str = "market_data.db", table_name: str = "eurusd_daily") -> pd.DataFrame:
    """Step 5: Read data from SQLite database"""
    print(f"\n=== Step 5: Reading data from database ({db_path} -> table '{table_name}') ===")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name} ORDER BY time ASC", conn)
    conn.close()
    
    df['time'] = pd.to_datetime(df['time'])
    print(f"Read {len(df)} rows from database.")
    print("Preview (first 3 rows):")
    print(df[['time', 'open', 'high', 'low', 'close', 'tick_volume']].head(3).to_string(index=False))
    print("Preview (last 3 rows):")
    print(df[['time', 'open', 'high', 'low', 'close', 'tick_volume']].tail(3).to_string(index=False))
    return df


def plot_candles(df: pd.DataFrame, output_image: str = "eurusd_candles.png", display_recent_bars: int = 150):
    """Step 6: Plot candlestick chart and overall trend"""
    print(f"\n=== Step 6: Plotting candlestick chart ===")
    
    fig, (ax_main, ax_recent) = plt.subplots(
        2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [1.2, 1.8]}
    )
    fig.suptitle("EURUSD Daily Data (2018 - Present)", fontsize=16, fontweight='bold')
    
    # --- Top Subplot: Long-term overview (2018 - Present) ---
    ax_main.plot(df['time'], df['close'], label='Daily Close', color='#1f77b4', linewidth=1.2)
    ax_main.plot(df['time'], df['close'].rolling(window=50).mean(), label='50-day SMA', color='#ff7f0e', linestyle='--', linewidth=1.0)
    ax_main.plot(df['time'], df['close'].rolling(window=200).mean(), label='200-day SMA', color='#2ca02c', linestyle='--', linewidth=1.0)
    ax_main.set_title("Long-Term Trend (2018 - Today)")
    ax_main.set_ylabel("Price (USD)")
    ax_main.grid(True, linestyle=':', alpha=0.6)
    ax_main.legend(loc='upper right')
    ax_main.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    
    # --- Bottom Subplot: Detailed Candlestick View of Recent Period ---
    recent_df = df.tail(display_recent_bars).copy().reset_index(drop=True)
    recent_df['date_num'] = mdates.date2num(recent_df['time'])
    
    width = 0.6  # candle bar width in days
    
    # Bullish candles (Close >= Open)
    bulls = recent_df[recent_df['close'] >= recent_df['open']]
    # Bearish candles (Close < Open)
    bears = recent_df[recent_df['close'] < recent_df['open']]
    
    # Plot wicks (high-low lines)
    ax_recent.vlines(bulls['date_num'], bulls['low'], bulls['high'], color='#26a69a', linewidth=1)
    ax_recent.vlines(bears['date_num'], bears['low'], bears['high'], color='#ef5350', linewidth=1)
    
    # Plot bodies (rectangles / bar)
    ax_recent.bar(
        bulls['date_num'], bulls['close'] - bulls['open'],
        bottom=bulls['open'], width=width, color='#26a69a', edgecolor='#26a69a'
    )
    ax_recent.bar(
        bears['date_num'], bears['open'] - bears['close'],
        bottom=bears['close'], width=width, color='#ef5350', edgecolor='#ef5350'
    )
    
    start_str = recent_df['time'].iloc[0].strftime('%b %Y')
    end_str = recent_df['time'].iloc[-1].strftime('%b %Y')
    ax_recent.set_title(f"Detailed Candlesticks (Recent {display_recent_bars} Days: {start_str} - {end_str})")
    ax_recent.set_ylabel("Price (USD)")
    ax_recent.set_xlabel("Date")
    ax_recent.grid(True, linestyle=':', alpha=0.6)
    ax_recent.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    
    plt.tight_layout()
    plt.savefig(output_image, dpi=150)
    print(f"Candlestick chart saved successfully to '{output_image}'.")
    
    # Show interactive window if running in desktop GUI environment
    try:
        if os.environ.get("DISPLAY") or os.name == 'nt':
            plt.show(block=False)
            plt.pause(2)
    except Exception as e:
        print(f"Note: Displaying window skipped: {e}")
    finally:
        plt.close(fig)


def main():
    try:
        # Step 1: Initialize MT5
        initialize_mt5()
        
        # Step 2: Log in
        login_mt5()
        
        # Step 3: Download EURUSD (2018-today)
        df_downloaded = download_eurusd_data(start_year=2018)
        
        # Step 4: Save to database
        db_file = "market_data.db"
        table_name = "eurusd_daily"
        save_to_database(df_downloaded, db_path=db_file, table_name=table_name)
        
        # Step 5: Read database
        df_loaded = read_from_database(db_path=db_file, table_name=table_name)
        
        # Step 6: Plot candles
        plot_candles(df_loaded, output_image="eurusd_candles.png")
        
        print("\n=== Pipeline Completed Successfully! ===")
        
    finally:
        # Clean shutdown of MT5 connection
        mt5.shutdown()
        print("MT5 connection shut down.")


if __name__ == "__main__":
    main()
