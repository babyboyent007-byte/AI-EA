import pandas as pd
from .mt5_client import MT5Client
from ..database.repositories import CandleRepository
from .validator import DataValidator

class DownloaderOrchestrator:
    """Coordinates the incremental ingestion loop."""
    def __init__(self, client: MT5Client, repo: CandleRepository):
        self.client = client
        self.repo = repo
        self.validator = DataValidator()

    def sync_symbol(self, symbol: str, timeframe: str, timeframe_id: int):
        """Checks DB state and fetches missing data from MT5."""
        latest_ts = self.repo.get_latest_timestamp(symbol, timeframe)
        print(f'[Downloader] Syncing {symbol} {timeframe}... (Last TS: {latest_ts})')
        
        # Fetch fresh data (using count=500 for bootstrap/incremental)
        raw_data = self.client.fetch_candles(symbol, timeframe_id, 500)
        
        if not raw_data.empty and self.validator.validate_ohlc(raw_data):
            self.repo.save_candles(raw_data)
            print(f'[Downloader] {symbol} saved to relational store.')
        else:
            print(f'[Downloader] No new valid data for {symbol}.')