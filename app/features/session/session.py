import pandas as pd
import numpy as np
from ..base_feature import BaseFeature

class SessionFeature(BaseFeature):
    """Session Family: Time Encoding."""
    @property
    def name(self) -> str: return 'hour_sin_cos'

    @property
    def category(self) -> str: return 'session'

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        processed_df = df.copy()
        if 'timestamp' in processed_df.columns:
            ts = pd.to_datetime(processed_df['timestamp'])
            processed_df['hour_sin'] = np.sin(2 * np.pi * ts.dt.hour / 24)
            processed_df['hour_cos'] = np.cos(2 * np.pi * ts.dt.hour / 24)
        return processed_df