import pandas as pd

class TradingLogic:
    def __init__(self):
        # Configurable instrument settings
        self.settings = {
            'EURUSD': {'pip_value': 0.0001, 'contract_size': 100000, 'min_hold': 120},
            'GBPUSD': {'pip_value': 0.0001, 'contract_size': 100000, 'min_hold': 120},
            'USDJPY': {'pip_value': 0.01,   'contract_size': 100000, 'min_hold': 120},
            'XAUUSD': {'pip_value': 0.01,   'contract_size': 100,    'min_hold': 120}
        }

    def get_signal_params(self, symbol):
        return self.settings.get(symbol, {'pip_value': 0.0001, 'contract_size': 100000, 'min_hold': 120})

    def evaluate_entry(self, symbol, ai_score, regime):
        """
        M5/M15 specific entry filter.
        Medium frequency usually requires regime alignment.
        """
        if regime == 'HIGH_VOLATILITY':
            return ai_score > 75  # Stricter entry in high vol
        return ai_score > 65      # Standard entry

if __name__ == '__main__':
    print('Trading Logic V1.0 (Forex/Gold) initialized.')
