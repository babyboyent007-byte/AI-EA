import numpy as np

class RiskManager:
    def __init__(self, max_dd_limit=0.25, account_leverage_cap=20):
        self.max_dd_limit = max_dd_limit
        self.leverage_cap = account_leverage_cap
        self.peak_equity = 1.0
        self.current_drawdown = 0.0
        self.is_halted = False

    def calculate_dynamic_size(self, current_equity, win_prob, rr_ratio, atr, volatility_scalar=0.1, kelly_fraction=0.5):
        """
        Calculates the risk-adjusted size scalar (0.0 to 1.0+).
        Determined by Kelly Criterion, Volatility, and Drawdown proximity.
        """
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
        self.current_drawdown = (self.peak_equity - current_equity) / self.peak_equity

        if self.current_drawdown >= (self.max_dd_limit * 0.9):
            self.is_halted = True
            return 0.0

        edge = win_prob - ((1 - win_prob) / rr_ratio) if rr_ratio > 0 else 0
        base_kelly = max(0, edge * kelly_fraction)
        vol_multiplier = 1.0 / (1.0 + (atr * volatility_scalar))
        dd_buffer = (self.max_dd_limit - self.current_drawdown) / self.max_dd_limit

        final_scalar = base_kelly * vol_multiplier * dd_buffer
        return round(max(0.0, final_scalar), 4)

    def calculate_max_allowed_lot(self, current_equity, risk_scalar, symbol_price, contract_size=100000):
        """
        Converts risk scalar to actual lot size.
        Ensures position does not exceed the risk model OR the hard leverage cap.
        """
        # 10x multiplier scales the Kelly/Vol scalar to a reasonable effective leverage range
        risk_weighted_notional = current_equity * risk_scalar * 10

        # Hard Leverage Cap check (safety floor)
        max_leverage_notional = current_equity * self.leverage_cap
        final_notional = min(risk_weighted_notional, max_leverage_notional)

        # Convert Notional USD/Quote to Lots
        lots = final_notional / (symbol_price * contract_size)
        return round(max(0.01, lots), 2)

if __name__ == '__main__':
    print('v1.8 Risk Engine: Risk-weighted lot sizing enabled (Leverage Cap: 20x).')
