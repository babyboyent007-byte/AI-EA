import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timezone
import os

def download_data():
    if not mt5.initialize():
        print('MT5 Initialization Failed')
        return

    symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF', 'XAUUSD']
    timeframes = {
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'H1': mt5.TIMEFRAME_H1
    }
    
    utc_from = datetime(2018, 1, 1, tzinfo=timezone.utc)
    utc_to = datetime.now(timezone.utc)

    for symbol in symbols:
        for tf_name, tf_val in timeframes.items():
            print(f'Downloading {symbol} {tf_name}...')
            rates = mt5.copy_rates_range(symbol, tf_val, utc_from, utc_to)
            
            if rates is not None and len(rates) > 0:
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                filename = f'data/historical/{symbol}_{tf_name}.csv'
                df.to_csv(filename, index=False)
                print(f'Saved {len(df)} rows to {filename}')
            else:
                print(f'Failed to fetch data for {symbol} {tf_name}')

    mt5.shutdown()

if __name__ == '__main__':
    download_data()