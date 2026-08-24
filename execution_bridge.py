import time
from datetime import datetime, timedelta
import MetaTrader5 as mt5 # Re-import MetaTrader5

class MT5ExecutionBridge:
    def __init__(self, risk_manager, broker='LiteFinance'):
        self.risk_manager = risk_manager
        self.broker = broker
        self.min_holding_time = 180
        self.active_positions = {}

    def get_account_info(self):
        """
        Retrieves current account equity and deposit utilization from MetaTrader5.
        Returns (current_equity, current_deposit_utilization) or (None, None) if not available.
        """
        if not mt5.initialize():
            print(f"[MT5 INFO] MT5 initialization failed: {mt5.last_error()}")
            return None, None

        account_info = mt5.account_info()
        if account_info:
            current_equity = account_info.equity
            margin_used = account_info.margin
            current_deposit_utilization = margin_used / current_equity if current_equity != 0 else 0.0
            # mt5.shutdown() # Shutdown after fetching info if not maintained persistently
            return current_equity, current_deposit_utilization
        else:
            print(f"[MT5 INFO] Failed to get account info: {mt5.last_error()}")
            # mt5.shutdown() # Shutdown after fetching info if not maintained persistently
            return None, None

    def execute_signal(self, symbol, score, current_price, win_prob, trade_sizing_multiplier=1.0):
        # No check for score < 70 here, as trade_sizing_multiplier already handles entry decision
        if trade_sizing_multiplier <= 0: # If multiplier is 0 or negative, no trade
            return "NO_ACTION"

        current_equity, current_deposit_utilization = self.get_account_info()
        if current_equity is None or current_deposit_utilization is None:
            print("[EXECUTION BRIDGE] Could not retrieve account metrics. Halting signal execution.")
            return "ACCOUNT_METRICS_UNAVAILABLE"

        # Dynamic sizing via Risk Engine, passing the trade_sizing_multiplier directly
        final_risk_scalar = self.risk_manager.calculate_dynamic_size(
            current_equity=current_equity, # Use dynamic equity
            current_deposit_utilization=current_deposit_utilization, # Pass deposit utilization
            win_prob=win_prob,
            rr_ratio=2.0,
            atr=current_price * 0.01,
            trade_sizing_multiplier=trade_sizing_multiplier # Pass directly
        )

        if final_risk_scalar <= 0:
            print(f"[EXECUTION BRIDGE] Final risk scalar is zero or less ({final_risk_scalar}). Halting signal execution.")
            return "HALTED_BY_RISK"

        lots = self.risk_manager.calculate_max_allowed_lot(current_equity, final_risk_scalar, current_price)

        print(f"[{self.broker}] Sending BUY for {symbol}: {lots} lots @ {current_price:.2f}")

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

        print(f"[{self.broker}] Closing {symbol} position. Holding time {int(elapsed)}s met rule.")
        del self.active_positions[symbol]
        return "POSITION_CLOSED"