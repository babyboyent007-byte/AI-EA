import pandas as pd
import importlib
import pkgutil
import os
from .base_feature import BaseFeature

class UnifiedFeatureFactory:
    """
    Aggregator for all modular feature families.
    Dynamically discovers and executes modules within the features/ package.
    Enforces dependency validation based on feature metadata.
    """

    def __init__(self, enabled_features=None):
        """
        Args:
            enabled_features: Optional list of feature names to load.
        """
        self.features = []
        self.enabled_features = enabled_features
        self._discover_features()

    def _discover_features(self):
        package_path = os.path.dirname(__file__)
        for _, name, is_pkg in pkgutil.walk_packages([package_path], prefix='features.'):
            if not is_pkg:
                try:
                    module = importlib.import_module(name)
                    for attribute_name in dir(module):
                        attribute = getattr(module, attribute_name)
                        if isinstance(attribute, type) and issubclass(attribute, BaseFeature) and attribute is not BaseFeature:
                            feature_instance = attribute()
                            if self.enabled_features is None or feature_instance.name in self.enabled_features:
                                self.features.append(feature_instance)
                except Exception as e:
                    print(f"Skipping module {name}: {e}")

    def build_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validates dependencies and computes all registered features sequentially.
        """
        output_df = df.copy()
        for feature in self.features:
            # Metadata-Driven Dependency Verification
            missing = [col for col in feature.requires if col not in output_df.columns]
            if missing:
                print(f"⚠️ Warning: Skipping {feature.name} v{feature.version}. Missing dependencies: {missing}")
                continue
            
            output_df = feature.compute(output_df)
        return output_df
