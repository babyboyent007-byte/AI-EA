import pandas as pd
import numpy as np

class DatasetValidator:
    """Institutional-grade data integrity checks."""
    @staticmethod
    def check_for_leakage(df: pd.DataFrame, label_col='target_buy'):
        """Verifies that no labels are shifted or duplicated in features."""
        # Basic correlation check - highly suspicious if 1.0
        correlations = df.corr()[label_col].drop(label_col)
        leaky_cols = correlations[correlations.abs() > 0.99].index.tolist()
        if leaky_cols:
            print(f'[Validator] ⚠️ Potential Leakage detected in: {leaky_cols}')
        return leaky_cols

    @staticmethod
    def clean_nan_inf(df: pd.DataFrame) -> pd.DataFrame:
        """Final scrub of non-finite values."""
        initial_len = len(df)
        cleaned = df.replace([np.inf, -np.inf], np.nan).dropna()
        print(f'[Validator] Cleaned {initial_len - len(cleaned)} invalid rows.')
        return cleaned