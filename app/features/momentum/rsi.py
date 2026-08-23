import pandas as pd
import numpy as np
from ..base_feature import BaseFeature

class RSIFeature(BaseFeature):
    """Momentum Family: Relative Strength Index."""
    def __init__(self, period=14):
        self.period = period

    @property
    def name(self) -> str: return f'rsi_{self.period}'

    @property
    def category(self) -> str: return 'momentum'

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        processed_df = df.copy()
        delta = processed_df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / (loss + 1e-9)
        processed_df[self.name] = 100 - (100 / (1 + rs))
        return processed_df