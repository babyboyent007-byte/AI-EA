"""
Database schema definitions for the AI EA trading system.
Contains table definitions, constraints, and index creation statements.
Automatically creates all required tables:
- candles: OHLCV, spread, and tick/real volume market data
- indicators: Technical indicator values (EMA20, EMA50, RSI14, ATR14, ADX, MACD, ...)
- features: ML feature values in key-value format (BarID, FeatureName, FeatureValue)
- predictions: Model output probabilities, expected returns, and confidence
- trades: Executed and closed trades (Entry, Exit, SL, TP, Lots, Profit, Commission, Swap, Reason, AI Version)
- account_history: Periodic balance, equity, and margin tracking
- model_versions: Registered AI model artifacts, hyperparameters, and metrics
- backtest_results: Historical performance and backtest evaluation metrics
"""

from typing import List

# Schema version
SCHEMA_VERSION = "1.1.0"

# 1. Candles Table
CREATE_CANDLES_TABLE = """
CREATE TABLE IF NOT EXISTS candles (
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    time INTEGER NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    tick_volume INTEGER,
    spread INTEGER,
    real_volume INTEGER,
    PRIMARY KEY (symbol, timeframe, time)
);
"""

# 2. Indicators Table (Stores EMA20, EMA50, RSI14, ATR14, ADX, MACD, etc.)
CREATE_INDICATORS_TABLE = """
CREATE TABLE IF NOT EXISTS indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    time INTEGER NOT NULL,
    indicator_name TEXT NOT NULL,
    value REAL,
    params TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (symbol, timeframe, time, indicator_name)
);
"""

# 3. Features Table (Key-value design: BarID, FeatureName, FeatureValue)
CREATE_FEATURES_TABLE = """
CREATE TABLE IF NOT EXISTS features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bar_id INTEGER,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    time INTEGER NOT NULL,
    feature_name TEXT NOT NULL,
    feature_value REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (symbol, timeframe, time, feature_name)
);
"""

# 4. Predictions Table (ModelVersion, ProbabilityBuy, ProbabilitySell, ExpectedReturn, Confidence, Timestamp)
CREATE_PREDICTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    timeframe TEXT,
    timestamp INTEGER NOT NULL,
    model_version TEXT NOT NULL,
    probability_buy REAL,
    probability_sell REAL,
    expected_return REAL,
    confidence REAL,
    prediction_type TEXT,
    prediction_value REAL,
    probability REAL,
    features_snapshot TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 5. Trades Table (Entry, Exit, SL, TP, Lots, Profit, Commission, Swap, Reason, AI Version)
CREATE_TRADES_TABLE = """
CREATE TABLE IF NOT EXISTS trades (
    ticket INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    trade_type TEXT NOT NULL,
    lots REAL NOT NULL,
    volume REAL,
    entry_price REAL NOT NULL,
    entry_time INTEGER NOT NULL,
    open_price REAL,
    open_time INTEGER,
    exit_price REAL,
    exit_time INTEGER,
    close_price REAL,
    close_time INTEGER,
    sl REAL,
    tp REAL,
    profit REAL DEFAULT 0.0,
    commission REAL DEFAULT 0.0,
    swap REAL DEFAULT 0.0,
    reason TEXT,
    comment TEXT,
    ai_version TEXT,
    model_version TEXT,
    magic_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 6. Account History Table
CREATE_ACCOUNT_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS account_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    balance REAL NOT NULL,
    equity REAL NOT NULL,
    margin REAL,
    free_margin REAL,
    margin_level REAL,
    profit REAL,
    currency TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 7. Model Versions Table
CREATE_MODEL_VERSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS model_versions (
    model_id TEXT PRIMARY KEY,
    model_name TEXT NOT NULL,
    version TEXT NOT NULL,
    algorithm TEXT,
    hyperparameters TEXT,
    features_list TEXT,
    target_metric REAL,
    metrics_json TEXT,
    model_path TEXT,
    trained_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active'
);
"""

# 8. Backtest Results Table
CREATE_BACKTEST_RESULTS_TABLE = """
CREATE TABLE IF NOT EXISTS backtest_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backtest_name TEXT NOT NULL,
    model_id TEXT,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    start_date INTEGER NOT NULL,
    end_date INTEGER NOT NULL,
    initial_balance REAL,
    final_balance REAL,
    total_net_profit REAL,
    profit_factor REAL,
    sharpe_ratio REAL,
    max_drawdown REAL,
    max_drawdown_pct REAL,
    total_trades INTEGER,
    win_rate REAL,
    parameters TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Index Definitions for Query Optimization
INDICES: List[str] = [
    "CREATE INDEX IF NOT EXISTS idx_candles_lookup ON candles(symbol, timeframe, time);",
    "CREATE INDEX IF NOT EXISTS idx_indicators_lookup ON indicators(symbol, timeframe, time);",
    "CREATE INDEX IF NOT EXISTS idx_features_lookup ON features(symbol, timeframe, time);",
    "CREATE INDEX IF NOT EXISTS idx_features_bar ON features(bar_id);",
    "CREATE INDEX IF NOT EXISTS idx_predictions_lookup ON predictions(symbol, timeframe, timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_predictions_model ON predictions(model_version);",
    "CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol, entry_time);",
    "CREATE INDEX IF NOT EXISTS idx_trades_model ON trades(ai_version);",
    "CREATE INDEX IF NOT EXISTS idx_account_history_time ON account_history(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_backtest_model ON backtest_results(model_id);"
]

# All Table Statements in creation order
ALL_TABLES: List[str] = [
    CREATE_CANDLES_TABLE,
    CREATE_INDICATORS_TABLE,
    CREATE_FEATURES_TABLE,
    CREATE_PREDICTIONS_TABLE,
    CREATE_TRADES_TABLE,
    CREATE_ACCOUNT_HISTORY_TABLE,
    CREATE_MODEL_VERSIONS_TABLE,
    CREATE_BACKTEST_RESULTS_TABLE
]
