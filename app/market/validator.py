import pandas as pd

class DataValidator:
    """Institutional candle integrity checker."""
    @staticmethod
    def validate_ohlc(df: pd.DataFrame) -> bool:
        """Verifies logical price sequences (High >= Open/Close, etc.)."""
        if df.empty: return False
        
        valid = (
            (df['high'] >= df['open']) &
            (df['high'] >= df['close']) &
            (df['low'] <= df['open']) &
            (df['low'] <= df['close'])
        ).all()
        
        return valid