import pandas as pd
import numpy as np

class RegimeDetector:
    def __init__(self, trend_window=50, vol_window=20):
        self.trend_window = trend_window
        self.vol_window = vol_window

    def detect(self, df):
        if len(df) < self.trend_window:
            return 'INSUFFICIENT_DATA'

        df['sma_fast'] = df['close'].rolling(window=20).mean()
        df['sma_slow'] = df['close'].rolling(window=50).mean()
        df['std_dev'] = df['close'].rolling(window=self.vol_window).std()
        avg_vol = df['std_dev'].mean()

        fast_ma = df['sma_fast'].iloc[-1]
        slow_ma = df['sma_slow'].iloc[-1]
        current_vol = df['std_dev'].iloc[-1]

        if current_vol > avg_vol * 2.0:
            return 'HIGH_VOLATILITY'
        if fast_ma > slow_ma * 1.005:
            return 'TRENDING_UP'
        elif fast_ma < slow_ma * 0.995:
            return 'TRENDING_DOWN'
        else:
            return 'RANGE_BOUND'
