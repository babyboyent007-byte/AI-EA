import pandas as pd
from typing import Dict, List, Callable
from .base_feature import BaseFeature

class FeatureRegistry:
    def __init__(self):
        self._features: Dict[str, BaseFeature] = {}

    def register(self, feature: BaseFeature):
        self._features[feature.name] = feature

    def get_feature(self, name: str) -> BaseFeature:
        return self._features.get(name)

    def list_features(self) -> List[str]:
        return list(self._features.keys())

    def compute_all(self, df: pd.DataFrame) -> pd.DataFrame:
        output_df = df.copy()
        for name, feature in self._features.items():
            # Dependency Check
            missing = [col for col in feature.requires if col not in output_df.columns]
            if not missing:
                output_df = feature.compute(output_df)
            else:
                print(f'Warning: Skipping {name}, missing requirements: {missing}')
        return output_df