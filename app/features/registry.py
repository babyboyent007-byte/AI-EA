from typing import Dict, List
from .base_feature import BaseFeature

class FeatureRegistry:
    """Discovery mechanism for modular feature plugins."""
    def __init__(self):
        self._features: Dict[str, BaseFeature] = {}

    def register(self, feature: BaseFeature):
        self._features[feature.name] = feature
        print(f'[Registry] Registered: {feature.name} ({feature.category})')

    def get_all(self) -> List[BaseFeature]:
        return list(self._features.values())

    def get_by_category(self, category: str) -> List[BaseFeature]:
        return [f for f in self._features.values() if f.category == category]