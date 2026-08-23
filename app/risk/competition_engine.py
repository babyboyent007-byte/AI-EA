import numpy as np

class CompetitionRiskEngine:
    """
    Layer 5: Competition-Aware Risk Management.
    Dynamically adjusts risk-per-trade and confidence gating based on competition standing.
    """
    def __init__(self, max_dd_limit=0.25):
        self.max_dd_limit = max_dd_limit
        self.mode = 'GROWTH'

    def determine_regime(self, current_equity, leader_equity, drawdown):
        # 1. Defense Mode: Protect competitive standing or account safety
        if drawdown > (self.max_dd_limit * 0.75):
            self.mode = 'DEFENSE'
        elif current_equity > (leader_equity * 0.95):
            self.mode = 'DEFENSE'
        
        # 2. Attack Mode: Aggressive gap closing
        elif current_equity < (leader_equity * 0.75):
            self.mode = 'ATTACK'
        
        # 3. Growth Mode: Standard logarithmic growth
        else:
            self.mode = 'GROWTH'
            
        return self.mode

    def get_risk_params(self):
        configs = {
            'GROWTH':  {'risk_pct': 0.02, 'min_conf': 0.70, 'leverage': 1.0},
            'ATTACK':  {'risk_pct': 0.05, 'min_conf': 0.65, 'leverage': 2.5},
            'DEFENSE': {'risk_pct': 0.01, 'min_conf': 0.85, 'leverage': 0.5}
        }
        return configs.get(self.mode, configs['GROWTH'])