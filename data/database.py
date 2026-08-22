import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "market_data.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Candles table
    cursor.execute("""
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
        PRIMARY KEY(symbol, timeframe, time)
    )
    """)

    # 2. Indicators table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS indicators (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        time INTEGER NOT NULL,
        indicator_name TEXT NOT NULL,
        value REAL,
        params TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(symbol, timeframe, time, indicator_name)
    )
    """)

    # 3. Features table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS features (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        time INTEGER NOT NULL,
        feature_name TEXT NOT NULL,
        feature_value REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(symbol, timeframe, time, feature_name)
    )
    """)

    # 4. Predictions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        time INTEGER NOT NULL,
        model_version TEXT NOT NULL,
        prediction_type TEXT,
        prediction_value REAL,
        probability REAL,
        confidence REAL,
        features_snapshot TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 5. Trades table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        ticket INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL,
        trade_type TEXT NOT NULL,
        volume REAL NOT NULL,
        open_time INTEGER NOT NULL,
        open_price REAL NOT NULL,
        sl REAL,
        tp REAL,
        close_time INTEGER,
        close_price REAL,
        profit REAL,
        commission REAL,
        swap REAL,
        magic_number INTEGER,
        comment TEXT,
        model_version TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 6. Account history table
    cursor.execute("""
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
    )
    """)

    # 7. Model versions table
    cursor.execute("""
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
    )
    """)

    # 8. Backtest results table
    cursor.execute("""
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
    )
    """)

    # Useful indices for fast query performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_candles_lookup ON candles(symbol, timeframe, time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_indicators_lookup ON indicators(symbol, timeframe, time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_features_lookup ON features(symbol, timeframe, time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_lookup ON predictions(symbol, timeframe, time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol, open_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_account_history_time ON account_history(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_backtest_model ON backtest_results(model_id)")

    conn.commit()
    conn.close()
