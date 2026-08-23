import pandas as pd
import ccxt
from datetime import datetime

def fetch_historical_data(symbol='EURUSD', timeframe='M15', limit=100):
    try:
        exchange = ccxt.kraken()
        if '/' not in symbol:
            if symbol == 'XAUUSD': normalized_symbol = 'PAXG/USD'
            elif len(symbol) == 6: normalized_symbol = f'{symbol[:3]}/{symbol[3:]}'
            else: normalized_symbol = symbol
        else: normalized_symbol = symbol

        ohlcv = exchange.fetch_ohlcv(normalized_symbol, timeframe='15m', limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f'Error fetching {symbol}: {e}')
        return pd.DataFrame()
