import pandas as pd
import numpy as np
from ..base_feature import BaseFeature

class ATRFeature(BaseFeature):
    """Volatility Family: Average True Range (ATR)."""
    def __init__(self, period=14):
        self.period = period

    @property
    def name(self) -> str: return f'atr_{self.period}'

    @property
    def category(self) -> str: return 'volatility'

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        processed_df = df.copy()
        high_low = processed_df['high'] - processed_df['low']
        high_close = np.abs(processed_df['high'] - processed_df['close'].shift())
        low_close = np.abs(processed_df['low'] - processed_df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        processed_df[self.name] = true_range.rolling(self.period).mean()
        return processed_df