import pandas as pd
import numpy as np

class RegimeDetector:
    def __init__(self, trend_window=50, vol_window=20):
        self.trend_window = trend_window
        self.vol_window = vol_window

    def detect(self, df):
        if len(df) < self.trend_window: return 'INSUFFICIENT_DATA'
        df['sma_fast'] = df['close'].rolling(window=20).mean()
        df['sma_slow'] = df['close'].rolling(window=self.trend_window).mean()
        df['std_dev'] = df['close'].rolling(window=self.vol_window).std()
        avg_vol = df['std_dev'].mean()
        fast_ma, slow_ma, cur_vol = df['sma_fast'].iloc[-1], df['sma_slow'].iloc[-1], df['std_dev'].iloc[-1]
        if cur_vol > avg_vol * 2.5: return 'HIGH_VOLATILITY'
        if fast_ma > slow_ma * 1.005: return 'TRENDING_UP'
        if fast_ma < slow_ma * 0.995: return 'TRENDING_DOWN'
        return 'RANGE_BOUND'