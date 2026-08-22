import time
from datetime import datetime, timedelta

class MT5ExecutionBridge:
    def __init__(self, risk_manager, broker='LiteFinance'):
        self.risk_manager = risk_manager
        self.broker = broker
        # Enforcing a 3-minute safety holding time (180 seconds)
        self.min_holding_time = 180
        self.active_positions = {}

    def execute_signal(self, symbol, score, current_price, win_prob):
        if score < 70:
            return "NO_ACTION"

        # Dynamic sizing via Risk Engine
        risk_scalar = self.risk_manager.calculate_dynamic_size(
            current_equity=100000,
            win_prob=win_prob,
            rr_ratio=2.0,
            atr=current_price * 0.01
        )

        if risk_scalar <= 0:
            return "HALTED_BY_RISK"

        lots = self.risk_manager.calculate_max_allowed_lot(100000, risk_scalar, current_price)

        print(f"[{self.broker}] Sending BUY for {symbol}: {lots} lots @ {current_price}")

        # Track entry timestamp for holding rule compliance
        self.active_positions[symbol] = {
            'entry_time': datetime.now(),
            'type': 'BUY',
            'lots': lots
        }

        return "ORDER_SENT"

    def close_position(self, symbol):
        if symbol not in self.active_positions:
            return "NO_POSITION"

        entry_time = self.active_positions[symbol]['entry_time']
        elapsed = (datetime.now() - entry_time).total_seconds()

        if elapsed < self.min_holding_time:
            wait_remaining = int(self.min_holding_time - elapsed)
            print(f"[HOLDING RULE] {symbol} close blocked. Must hold for {wait_remaining}s more.")
            return "HOLDING_TIME_RESTRAINT"

        print(f"[LiteFinance] Closing {symbol} position. Holding time {int(elapsed)}s met rule.")
        del self.active_positions[symbol]
        return "POSITION_CLOSED"
