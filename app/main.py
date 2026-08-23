import time
import sys
import os
from pathlib import Path

# Force PROJECT_ROOT into path for package-level imports
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.market.mt5_client import MT5Client
from app.database.repositories import CandleRepository
from app.market.downloader import DownloaderOrchestrator
from app.market.symbols import SYMBOLS, TIMEFRAMES
from app.config.settings import settings

def run_ingestion_cycle():
    print('--- [AI EA: Ingestion Cycle Started] ---')

    client = MT5Client(settings.SERVER, 0, 'pass')
    repo = CandleRepository(settings.DB_PATH)
    orchestrator = DownloaderOrchestrator(client, repo)

    if not client.connect():
        print('❌ MT5 Connection Failed.')
        return

    try:
        for symbol in SYMBOLS:
            for tf_name, tf_id in TIMEFRAMES:
                orchestrator.sync_symbol(symbol, tf_name, tf_id)
        print('✅ Cycle Complete.')
    finally:
        client.shutdown()

if __name__ == '__main__':
    run_ingestion_cycle()