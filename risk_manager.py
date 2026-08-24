import numpy as np

class RiskManager:
    def __init__(self, max_dd_limit=0.25, account_leverage_cap=20):
        self.max_dd_limit = max_dd_limit
        self.leverage_cap = account_leverage_cap
        self.peak_equity = 1.0
        self.current_drawdown = 0.0
        self.is_halted = False
        self.risk_thresholds = {
            'normal': (0.00, 0.05),
            'reduce_risk': (0.05, 0.08),
            'strong_reduction': (0.08, 0.12),
            'very_conservative': (0.12, 0.15),
            'emergency': (0.15, 0.20)
        }

    def get_current_drawdown_status(self, current_equity):
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
        self.current_drawdown = (self.peak_equity - current_equity) / self.peak_equity

        if self.current_drawdown >= self.risk_thresholds['emergency'][0]: return 'emergency'
        if self.current_drawdown >= self.risk_thresholds['very_conservative'][0]: return 'very_conservative'
        if self.current_drawdown >= self.risk_thresholds['strong_reduction'][0]: return 'strong_reduction'
        if self.current_drawdown >= self.risk_thresholds['reduce_risk'][0]: return 'reduce_risk'
        return 'normal'

    def calculate_dynamic_size(self, current_equity, current_deposit_utilization, win_prob, rr_ratio, atr, volatility_scalar=0.1, kelly_fraction=0.5, trade_sizing_multiplier=1.0):
        if current_equity > self.peak_equity: 
            self.peak_equity = current_equity
        self.current_drawdown = (self.peak_equity - current_equity) / self.peak_equity
        
        # 20% Hard Drawdown Circuit Breaker
        if self.current_drawdown >= 0.20:
            self.is_halted = True
            return 0.0
            
        # 30% Margin Utilization Cap
        if current_deposit_utilization >= 0.30:
            return 0.0

        edge = win_prob - ((1 - win_prob) / rr_ratio) if rr_ratio > 0 else 0
        base_kelly = max(0, edge * kelly_fraction)
        vol_multiplier = 1.0 / (1.0 + (atr * volatility_scalar))
        
        # Linear drawdown buffer relative to max_dd_limit (25%)
        dd_buffer = (self.max_dd_limit - self.current_drawdown) / self.max_dd_limit

        final_scalar = base_kelly * vol_multiplier * dd_buffer * trade_sizing_multiplier
        return round(max(0.0, final_scalar), 4)

    def calculate_max_allowed_lot(self, current_equity, risk_scalar, symbol_price, contract_size=100000):
        if risk_scalar <= 0: return 0.01 # Floor for heartbeat if needed
        
        # Apply risk-weighted notional vs leverage cap
        risk_weighted_notional = current_equity * risk_scalar * 10
        max_leverage_notional = current_equity * self.leverage_cap
        final_notional = min(risk_weighted_notional, max_leverage_notional)

        lots = final_notional / (symbol_price * contract_size) if symbol_price > 0 else 0.01
        return round(max(0.01, lots), 2)