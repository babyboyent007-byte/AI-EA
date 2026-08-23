import pandas as pd
from ..base_feature import BaseFeature

class EMAFeature(BaseFeature):
    """Trend Family: Exponential Moving Average Ribbon."""
    def __init__(self, spans=[10, 20, 50, 100, 200]):
        self.spans = spans

    @property
    def name(self) -> str: return 'ema_ribbon'

    @property
    def category(self) -> str: return 'trend'

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        processed_df = df.copy()
        for span in self.spans:
            col_name = f'ema_{span}'
            processed_df[col_name] = processed_df['close'].ewm(span=span, adjust=False).mean()
            # Normalized distance from price
            processed_df[f'dist_ema_{span}'] = (processed_df['close'] - processed_df[col_name]) / processed_df[col_name]
        return processed_df