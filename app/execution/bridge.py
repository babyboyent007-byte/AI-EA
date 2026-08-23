from datetime import datetime

class MT5ExecutionBridge:
    def __init__(self, risk_manager):
        self.risk_manager = risk_manager

    def execute(self, symbol, win_prob, price):
        if self.risk_manager.is_halted: return 'HALTED'
        action = 'BUY' if win_prob > 0.75 else 'SELL' if win_prob < 0.25 else 'WAIT'
        if action == 'WAIT': return 'NO_ACTION'
        return f'ORDER_SENT: {action} {symbol} @ {price}'