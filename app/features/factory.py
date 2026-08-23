import pandas as pd
from .registry import FeatureRegistry

class FeatureFactory:
    """Orchestrator for the Feature Engineering Pipeline."""
    def __init__(self, registry: FeatureRegistry):
        self.registry = registry

    def compute_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """Runs raw candles through every registered feature plugin."""
        if df.empty: return df
        
        processed_df = df.copy()
        features = self.registry.get_all()
        
        print(f'[Factory] Processing {len(features)} alpha features...')
        for feature in features:
            processed_df = feature.compute(processed_df)
            
        return processed_df