import pandas as pd
from pathlib import Path

class DatasetExporter:
    """Institutional data storage engine."""
    @staticmethod
    def save_parquet(df: pd.DataFrame, path: Path):
        """Saves as Parquet for fast I/O and schema preservation."""
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path, index=False)
        print(f'[Exporter] Saved dataset to: {path}')

    @staticmethod
    def save_csv(df: pd.DataFrame, path: Path):
        """Saves as CSV for human readability/audit."""
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        print(f'[Exporter] Saved audit CSV to: {path}')