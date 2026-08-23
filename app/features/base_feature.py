import pandas as pd
from abc import ABC, abstractmethod
from typing import List

class BaseFeature(ABC):
    """
    Core abstraction for the Feature Factory Architecture.
    Enforces metadata for documentation and dependency tracking.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def family(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @property
    @abstractmethod
    def requires(self) -> List[str]:
        """List of column names required for computation."""
        pass

    @abstractmethod
    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        pass
