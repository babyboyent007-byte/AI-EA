from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List

class SystemSettings(BaseSettings):
    # Core Paths
    BASE_DIR: Path = Path('/content/drive/MyDrive/AI_EA/app')
    DB_PATH: str = "sqlite:////content/drive/MyDrive/AI_EA/data/production_v2.db"
    LOG_DIR: Path = Path('/content/drive/MyDrive/AI_EA/logs')
    
    # Strategy Constants
    SYMBOLS: List[str] = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
    TIMEFRAME: str = 'M15'
    
    # Risk Parameters
    MAX_DRAWDOWN: float = 0.25
    LEVERAGE_CAP: int = 20
    
    class Config:
        env_file = ".env"

settings = SystemSettings()