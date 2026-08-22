import pandas as pd
import numpy as np
from datetime import datetime
import ccxt

def fetch_historical_data(symbol='EUR/USD', timeframe='M15', limit=100):
    """
    Fetches historical OHLCV data from Kraken.
    Supports Crypto, Forex, and Gold (XAU).
    """
    try:
        exchange = ccxt.kraken()

        # Advanced Symbol Normalization for Kraken
        normalized_symbol = symbol
        # Kraken Gold check: XAU/USD is often PAXG/USD or XAU/EUR
        if symbol == 'XAUUSD' or symbol == 'GOLD':
            # Standardizing to PAXG/USD as it is Kraken's primary Gold-linked instrument for USD
            normalized_symbol = 'PAXG/USD' 
        elif '/' not in symbol:
            if symbol == 'BTCUSDT':
                normalized_symbol = 'BTC/USDT'
            elif len(symbol) == 6:
                # Standard Forex 6-char to Kraken pair
                normalized_symbol = f'{symbol[:3]}/{symbol[3:]}'

        print(f'Fetching {limit} fresh {timeframe} candles for {normalized_symbol}...')
        tf_map = {'M5': '5m', 'M15': '15m', '1h': '1h', '4h': '4h'}
        api_tf = tf_map.get(timeframe, '15m')

        ohlcv = exchange.fetch_ohlcv(normalized_symbol, timeframe=api_tf, limit=limit)
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df = pd.DataFrame(ohlcv, columns=columns)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f'Error fetching {symbol} data: {e}')
        return pd.DataFrame()

if __name__ == '__main__':
    test_df = fetch_historical_data(symbol='XAUUSD', timeframe='M15', limit=5)
    print(test_df.head())