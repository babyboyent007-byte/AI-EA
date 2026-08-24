# AI EA Production Configuration
INSTRUMENTS = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'AUDUSD', 'USDCAD', 'USDCHF']
TIMEFRAME = 'M15'
RISK_PER_TRADE = 0.01
MAX_DD_LIMIT = 0.25
# Circuit breaker trigger for RiskManager
DD_CIRCUIT_BREAKER = 0.20
# Selected model from benchmarking
AI_MODEL_PATH = 'models/xgb_bench.joblib'
HEARTBEAT_DAYS = 9.5