import numpy as np

class RiskManager:
    def __init__(self, max_dd_limit=0.25):
        self.max_dd_limit = max_dd_limit
        self.peak_equity = 5000.0
        self.is_halted = False

    def calculate_size(self, current_equity, win_prob, atr):
        if current_equity > self.peak_equity: self.peak_equity = current_equity
        drawdown = (self.peak_equity - current_equity) / self.peak_equity
        if drawdown >= self.max_dd_limit: 
            self.is_halted = True
            return 0.0
        dd_buffer = (self.max_dd_limit - drawdown) / self.max_dd_limit
        return max(0.0, round((win_prob - 0.5) * 2 * dd_buffer, 4))