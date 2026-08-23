import pandas as pd
from ..base_feature import BaseFeature

class SwingFeature(BaseFeature):
    """Structure Family: Local Swing Identification."""
    @property
    def name(self) -> str: return 'is_swing'

    @property
    def category(self) -> str: return 'structure'

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        processed_df = df.copy()
        processed_df['is_swing_high'] = ((processed_df['high'] > processed_df['high'].shift(1)) & (processed_df['high'] > processed_df['high'].shift(-1))).astype(int)
        processed_df['is_swing_low'] = ((processed_df['low'] < processed_df['low'].shift(1)) & (processed_df['low'] < processed_df['low'].shift(-1))).astype(int)
        return processed_df