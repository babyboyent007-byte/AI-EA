import pandas as pd
import market.mt5_client as mt5_client
import database.repositories as repositories
import market.validator as validator

class DownloaderOrchestrator:
    """Coordinates the incremental ingestion loop using absolute imports."""
    def __init__(self, client, repo):
        self.client = client
        self.repo = repo
        self.validator = validator.DataValidator()

    def sync_symbol(self, symbol: str, timeframe: str, timeframe_id: int):
        latest_ts = self.repo.get_latest_timestamp(symbol, timeframe)
        print(f'[Downloader] Syncing {symbol} {timeframe}... (Last TS: {latest_ts})')
        raw_data = self.client.fetch_candles(symbol, timeframe_id, 500)

        if not raw_data.empty and self.validator.validate_ohlc(raw_data):
            self.repo.save_candles(raw_data)
            print(f'[Downloader] {symbol} saved to relational store.')
        else:
            print(f'[Downloader] No new valid data for {symbol}.')