import pandas as pd

class TradingLogic:
    def __init__(self, risk_manager=None):
        self.risk_manager = risk_manager
        self.mode = "GROWTH"  # Modes: GROWTH, ATTACK, DEFENSE
        self.settings = {
            "EURUSD": {"pip_value": 0.0001, "contract_size": 100000},
            "XAUUSD": {"pip_value": 0.01,   "contract_size": 100}
        }
        # Base thresholds by mode
        self.mode_config = {
            "GROWTH":  {"base_threshold": 65, "aggression": 1.0},
            "ATTACK":  {"base_threshold": 60, "aggression": 1.3},
            "DEFENSE": {"base_threshold": 75, "aggression": 0.7}
        }

    def set_competition_mode(self, mode):
        if mode in self.mode_config:
            self.mode = mode
            print(f"[LOGIC] Competition Mode shifted to {mode}")

    def evaluate_entry(self, symbol, ai_score, regime, current_equity=1.0):
        conf = self.mode_config[self.mode]
        entry_threshold = conf["base_threshold"]

        if self.risk_manager:
            status = self.risk_manager.get_current_drawdown_status(current_equity)
            if status != "normal":
                entry_threshold += 10 # Tighten during drawdown regardless of mode

        if ai_score > entry_threshold:
            # Calculate multiplier scaled by mode aggression
            multiplier = (1.0 + (ai_score - entry_threshold) / 100.0) * conf["aggression"]
            return round(max(0.1, multiplier), 2)
        return 0.0

if __name__ == '__main__':
    print('Trading Logic V2.0 (Competition Modes) initialized.')