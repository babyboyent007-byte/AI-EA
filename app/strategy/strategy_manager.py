import pandas as pd
from pathlib import Path
from typing import Dict, Any
from ..core.logger import setup_logger
from ..core import constants

class StrategyManager:
    def __init__(self, logger_path: Path):
        self.logger = setup_logger('StrategyManager', str(logger_path / 'strategy.log'))

    def evaluate_signal(self, symbol: str, features: pd.DataFrame, consensus_probs: list) -> Dict[str, Any]:
        """
        Evaluates AI consensus against strategy rules.
        avg_probs format: [SELL, NEUTRAL, BUY]
        """
        sell_p, neut_p, buy_p = consensus_probs
        
        # Logic gating for high-conviction entries
        if buy_p > 0.75:
            signal = constants.BUY
            confidence = buy_p
        elif sell_p > 0.75:
            signal = constants.SELL
            confidence = sell_p
        else:
            signal = constants.NONE
            confidence = neut_p
            
        self.logger.info(f'Evaluated {symbol}: Signal={signal}, Confidence={confidence:.2f}')
        
        return {
            'symbol': symbol,
            'signal': signal,
            'confidence': confidence,
            'action': 'EXECUTE' if signal != constants.NONE else 'FILTERED'
        }