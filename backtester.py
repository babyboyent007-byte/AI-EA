import pandas as pd
import numpy as np
from risk_manager import RiskManager
from trading_logic import TradingLogic

def run_backtest(df, initial_equity=100000, leverage=400):
    risk = RiskManager(max_dd_limit=0.25, account_leverage_cap=20)
    logic = TradingLogic(risk_manager=risk)
    
    equity = initial_equity
    equities = [equity]
    
    if 'score' not in df.columns: df['score'] = 75
    if 'regime' not in df.columns: df['regime'] = 'NORMAL'
    if 'win_prob' not in df.columns: df['win_prob'] = 0.52

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i-1]
        
        multiplier = logic.evaluate_entry('BACKTEST', row['score'], row['regime'], current_equity=equity)
        risk_scalar = risk.calculate_dynamic_size(equity, 0.05, row['win_prob'], 2.0, row['close']*0.01, trade_sizing_multiplier=multiplier)
        lots = risk.calculate_max_allowed_lot(equity, risk_scalar, row['close'])
        
        pnl = lots * 100000 * ((row['close'] / prev_row['close']) - 1) if multiplier > 0 else 0
        equity += pnl
        equities.append(equity)

    df['equity_curve'] = equities
    returns = pd.Series(equities).pct_change().dropna()
    
    # Competition Metrics
    total_return = (equity - initial_equity) / initial_equity
    max_drawdown = (pd.Series(equities).cummax() - pd.Series(equities)).max() / pd.Series(equities).cummax().max()
    
    # Sortino Ratio (Downside deviation only)
    downside_returns = returns[returns < 0]
    sortino = np.sqrt(252) * returns.mean() / downside_returns.std() if len(downside_returns) > 0 else 0
    
    # Calmar Ratio
    calmar = total_return / max_drawdown if max_drawdown > 0 else 0
    
    print('--- Backtest Performance Summary ---')
    print(f'Final Equity: ${equity:,.2f}')
    print(f'Total Return: {total_return:.2%}')
    print(f'Max Drawdown: {max_drawdown:.2%}')
    print(f'Sortino Ratio: {sortino:.2f}')
    print(f'Calmar Ratio: {calmar:.2f}')
    
    return df

if __name__ == "__main__":
    print("Backtester with Competition Metrics Ready.")