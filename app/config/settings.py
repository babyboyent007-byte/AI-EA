from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

class SystemSettings(BaseSettings):
    BASE_DIR: Path = Path('/content/drive/MyDrive/AI_EA/app')
    DB_PATH: Path = Path('/content/drive/MyDrive/AI_EA/data/production_v2.db')
    LOG_DIR: Path = Path('/content/drive/MyDrive/AI_EA/logs')
    
    # Strategy Constants
    SYMBOLS: List[str] = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
    
    # Broker Config
    SERVER: str = 'LiteFinance-MT5-Demo'
    BROKER_NAME: str = 'LiteFinance'

    class Config:
        arbitrary_types_allowed = True

settings = SystemSettings()