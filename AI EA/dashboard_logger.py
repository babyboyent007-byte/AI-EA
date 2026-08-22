import pandas as pd
import os
from datetime import datetime

class MultiAssetLogger:
    def __init__(self, log_dir):
        self.log_path = os.path.join(log_dir, 'multi_asset_logs.csv')
        if not os.path.exists(self.log_path):
            df = pd.DataFrame(columns=['timestamp', 'symbol', 'timeframe', 'price', 'regime', 'ai_score', 'action', 'lot_size'])
            df.to_csv(self.log_path, index=False)

    def log_event(self, symbol, timeframe, price, regime, score, action, lots):
        new_entry = pd.DataFrame([{
            'timestamp': datetime.now(),
            'symbol': symbol,
            'timeframe': timeframe,
            'price': price,
            'regime': regime,
            'ai_score': score,
            'action': action,
            'lot_size': lots
        }])
        new_entry.to_csv(self.log_path, mode='a', header=False, index=False)

if __name__ == '__main__':
    print('Multi-Asset Logger initialized.')
