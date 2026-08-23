import pandas as pd
from pathlib import Path
from .label_generator import TripleBarrierLabeler

class DatasetBuilder:
    """
    Consolidates SQL data and engineered features into training-ready dataframes.
    """
    def __init__(self, feature_columns: list):
        self.feature_columns = feature_columns
        self.labeler = TripleBarrierLabeler()

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Step 1: Apply Labels
        Step 2: Align with Features
        Step 3: Handle technical warm-up (NaNs)
        """
        # Generate labels
        labeled_df = self.labeler.generate_buy_labels(df)
        
        # Filter columns to only include features + target
        # Retaining 'timestamp' for time-series splitting later
        cols_to_keep = ['timestamp'] + self.feature_columns + ['target_buy']
        available_cols = [c for c in cols_to_keep if c in labeled_df.columns]
        
        dataset = labeled_df[available_cols].copy()
        
        # Final Cleanup
        dataset = dataset.replace([np.inf, -np.inf], np.nan).dropna()
        
        print(f'[Builder] Dataset generated. Rows: {len(dataset)} | Features: {len(self.feature_columns)}')
        return dataset