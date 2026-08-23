import pandas as pd
from abc import ABC, abstractmethod

class BaseFeature(ABC):
    """Institutional interface for all Alpha indicators."""
    
    @property
    @abstractmethod
    def name(self) -> str: pass

    @property
    @abstractmethod
    def category(self) -> str: pass

    @property
    def version(self) -> str: return '1.0.0'

    @abstractmethod
    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies indicator logic to the dataframe."""
        pass

    def validate(self, df: pd.DataFrame) -> bool:
        """Basic integrity check for the generated column."""
        if self.name not in df.columns:
            return False
        return not df[self.name].isnull().any()