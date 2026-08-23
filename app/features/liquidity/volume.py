import pandas as pd
from ..base_feature import BaseFeature

class VolumeFeature(BaseFeature):
    """Liquidity Family: Volume Metrics."""
    @property
    def name(self) -> str: return 'vol_sma_ratio'

    @property
    def category(self) -> str: return 'liquidity'

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        processed_df = df.copy()
        processed_df['vol_sma_20'] = processed_df['volume'].rolling(20).mean()
        processed_df[self.name] = processed_df['volume'] / (processed_df['vol_sma_20'] + 1e-9)
        return processed_df