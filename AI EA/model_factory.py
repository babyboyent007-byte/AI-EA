import xgboost as xgb
import numpy as np
from sklearn.metrics import accuracy_score

class ModelFactory:
    @staticmethod
    def get_xgb_baseline(params=None):
        """Returns a pre-configured XGBoost model for structured market data."""
        if params is None:
            params = {
                'n_estimators': 200,
                'max_depth': 5,
                'learning_rate': 0.05,
                'objective': 'binary:logistic',
                'random_state': 42
            }
        return xgb.XGBClassifier(**params)

    @staticmethod
    def rule_based_baseline(df):
        """Strict rule-based baseline: SMA Cross + RSI."""
        signals = np.zeros(len(df))
        # Simple trend + momentum rules
        bullish = (df['close'] > df['sma_20']) & (df['rsi_14'] < 70)
        bearish = (df['close'] < df['sma_20']) & (df['rsi_14'] > 30)
        
        signals[bullish] = 1
        signals[bearish] = -1
        return signals

if __name__ == '__main__':
    print('Model Factory (XGBoost & Rule-Based Baselines) initialized.')
