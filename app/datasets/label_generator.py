import pandas as pd
import numpy as np

class TripleBarrierLabeler:
    """
    Generates binary classification labels based on competition risk-reward constraints.
    Logic: If price hits (Current + 2*ATR) before (Current - 1*ATR) within N bars, label = 1.
    """
    def __init__(self, horizon=20, tp_mult=2.0, sl_mult=1.0):
        self.horizon = horizon
        self.tp_mult = tp_mult
        self.sl_mult = sl_mult

    def generate_buy_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Labels 1 if TP hit first, 0 otherwise."""
        processed_df = df.copy()
        
        # Ensure we have ATR for barrier calculation
        if 'atr_14' not in processed_df.columns:
            # Fallback internal ATR calculation if feature module not yet run
            high_low = processed_df['high'] - processed_df['low']
            high_close = np.abs(processed_df['high'] - processed_df['close'].shift())
            low_close = np.abs(processed_df['low'] - processed_df['close'].shift())
            processed_df['atr_14'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1).rolling(14).mean()

        labels = []
        
        for i in range(len(processed_df) - self.horizon):
            price = processed_df['close'].iloc[i]
            atr = processed_df['atr_14'].iloc[i]
            
            tp_barrier = price + (atr * self.tp_mult)
            sl_barrier = price - (atr * self.sl_mult)
            
            # Window of future prices
            window = processed_df.iloc[i+1 : i+1+self.horizon]
            
            label = 0
            for _, row in window.iterrows():
                if row['high'] >= tp_barrier:
                    label = 1
                    break
                if row['low'] <= sl_barrier:
                    label = 0
                    break
            labels.append(label)
            
        # Padding for the horizon end
        labels.extend([np.nan] * self.horizon)
        processed_df['target_buy'] = labels
        return processed_df.dropna(subset=['target_buy'])