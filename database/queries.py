"""
Database queries and helper operations for the AI EA system.
Provides type-safe, reusable data access methods for market candles, indicators,
features, predictions, trades, account history, models, and backtest results.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from .database import get_connection, get_db_context


def insert_candles(
    records: Union[pd.DataFrame, List[Dict[str, Any]], List[Tuple[Any, ...]]],
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """
    Insert or replace candle records in the database.
    
    Accepts a pandas DataFrame, list of dicts, or list of tuples.
    Expected columns/fields:
    symbol, timeframe, time, open, high, low, close, tick_volume, spread, real_volume
    """
    if isinstance(records, pd.DataFrame):
        data = records[[
            "symbol", "timeframe", "time", "open", "high", "low", "close",
            "tick_volume", "spread", "real_volume"
        ]].to_records(index=False).tolist()
    elif isinstance(records, list) and len(records) > 0 and isinstance(records[0], dict):
        data = [
            (
                r["symbol"], r["timeframe"], int(r["time"]), float(r["open"]),
                float(r["high"]), float(r["low"]), float(r["close"]),
                int(r.get("tick_volume", 0)), int(r.get("spread", 0)), int(r.get("real_volume", 0))
            )
            for r in records
        ]
    else:
        data = records  # Assumed list of tuples

    if not data:
        return 0

    sql = """
    INSERT OR REPLACE INTO candles (
        symbol, timeframe, time, open, high, low, close,
        tick_volume, spread, real_volume
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    if conn is not None:
        cursor = conn.cursor()
        cursor.executemany(sql, data)
        conn.commit()
        return len(data)

    with get_db_context(db_path=db_path) as context_conn:
        cursor = context_conn.cursor()
        cursor.executemany(sql, data)
        return len(data)


def get_candles(
    symbol: str,
    timeframe: str,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    limit: Optional[int] = None,
    as_df: bool = True,
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Fetch historical candles for a symbol and timeframe.
    """
    query = ["SELECT symbol, timeframe, time, open, high, low, close, tick_volume, spread, real_volume FROM candles WHERE symbol = ? AND timeframe = ?"]
    params: List[Any] = [symbol, timeframe]

    if start_time is not None:
        query.append("AND time >= ?")
        params.append(start_time)

    if end_time is not None:
        query.append("AND time <= ?")
        params.append(end_time)

    query.append("ORDER BY time ASC")

    if limit is not None:
        query.append(f"LIMIT {int(limit)}")

    sql_statement = " ".join(query)

    active_conn = conn or get_connection(db_path=db_path)
    try:
        if as_df:
            return pd.read_sql_query(sql_statement, active_conn, params=params)

        active_conn.row_factory = sqlite3.Row
        cursor = active_conn.cursor()
        cursor.execute(sql_statement, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if conn is None:
            active_conn.close()


def get_candle_count(
    symbol: Optional[str] = None,
    timeframe: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """Get total candle count, optionally filtered by symbol and timeframe."""
    sql = "SELECT COUNT(*) FROM candles"
    params: List[Any] = []
    conditions: List[str] = []

    if symbol:
        conditions.append("symbol = ?")
        params.append(symbol)
    if timeframe:
        conditions.append("timeframe = ?")
        params.append(timeframe)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    active_conn = conn or get_connection(db_path=db_path)
    try:
        cursor = active_conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return row[0] if row else 0
    finally:
        if conn is None:
            active_conn.close()


def get_available_symbols(
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """Get list of distinct symbols, timeframes, bar counts, and date ranges."""
    sql = """
    SELECT
        symbol,
        timeframe,
        COUNT(*) as total_bars,
        MIN(time) as start_time,
        MAX(time) as end_time,
        datetime(MIN(time), 'unixepoch') as start_date,
        datetime(MAX(time), 'unixepoch') as end_date
    FROM candles
    GROUP BY symbol, timeframe
    ORDER BY symbol, timeframe
    """
    active_conn = conn or get_connection(db_path=db_path, row_factory=sqlite3.Row)
    try:
        cursor = active_conn.cursor()
        cursor.execute(sql)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if conn is None:
            active_conn.close()


def insert_indicators(
    records: Union[pd.DataFrame, List[Dict[str, Any]]],
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """Insert indicator values into the database."""
    if isinstance(records, pd.DataFrame):
        data = records[["symbol", "timeframe", "time", "indicator_name", "value", "params"]].to_dict(orient="records")
    else:
        data = records

    if not data:
        return 0

    tuples = [
        (
            r["symbol"], r["timeframe"], int(r["time"]),
            r["indicator_name"], float(r["value"]) if r["value"] is not None else None,
            r.get("params")
        )
        for r in data
    ]

    sql = """
    INSERT OR REPLACE INTO indicators (
        symbol, timeframe, time, indicator_name, value, params
    ) VALUES (?, ?, ?, ?, ?, ?)
    """

    if conn is not None:
        cursor = conn.cursor()
        cursor.executemany(sql, tuples)
        conn.commit()
        return len(tuples)

    with get_db_context(db_path=db_path) as context_conn:
        cursor = context_conn.cursor()
        cursor.executemany(sql, tuples)
        return len(tuples)


def get_indicators(
    symbol: str,
    timeframe: str,
    indicator_name: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    as_df: bool = True,
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """Fetch indicator records for a symbol and timeframe."""
    query = ["SELECT id, symbol, timeframe, time, indicator_name, value, params, created_at FROM indicators WHERE symbol = ? AND timeframe = ?"]
    params: List[Any] = [symbol, timeframe]

    if indicator_name:
        query.append("AND indicator_name = ?")
        params.append(indicator_name)
    if start_time is not None:
        query.append("AND time >= ?")
        params.append(start_time)
    if end_time is not None:
        query.append("AND time <= ?")
        params.append(end_time)

    query.append("ORDER BY time ASC")
    sql_statement = " ".join(query)

    active_conn = conn or get_connection(db_path=db_path)
    try:
        if as_df:
            return pd.read_sql_query(sql_statement, active_conn, params=params)
        active_conn.row_factory = sqlite3.Row
        cursor = active_conn.cursor()
        cursor.execute(sql_statement, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if conn is None:
            active_conn.close()


def insert_features(
    records: Union[pd.DataFrame, List[Dict[str, Any]]],
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """
    Insert engineered feature values into the database.
    Supports key-value feature storage with BarID, FeatureName, FeatureValue,
    as well as symbol, timeframe, time/timestamp.
    """
    if isinstance(records, pd.DataFrame):
        data = records.to_dict(orient="records")
    else:
        data = records

    if not data:
        return 0

    tuples = [
        (
            r.get("bar_id") or r.get("BarID"),
            r.get("symbol", ""),
            r.get("timeframe", ""),
            int(r.get("time") or r.get("timestamp") or 0),
            r.get("feature_name") or r.get("FeatureName") or "",
            float(r.get("feature_value") or r.get("FeatureValue")) if (r.get("feature_value") is not None or r.get("FeatureValue") is not None) else None
        )
        for r in data
    ]

    sql = """
    INSERT OR REPLACE INTO features (
        bar_id, symbol, timeframe, time, feature_name, feature_value
    ) VALUES (?, ?, ?, ?, ?, ?)
    """

    if conn is not None:
        cursor = conn.cursor()
        cursor.executemany(sql, tuples)
        conn.commit()
        return len(tuples)

    with get_db_context(db_path=db_path) as context_conn:
        cursor = context_conn.cursor()
        cursor.executemany(sql, tuples)
        return len(tuples)


def get_features(
    symbol: Optional[str] = None,
    timeframe: Optional[str] = None,
    feature_name: Optional[str] = None,
    bar_id: Optional[int] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    as_df: bool = True,
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """Fetch feature records for a symbol, timeframe, or bar_id."""
    query = ["SELECT id, bar_id, symbol, timeframe, time, feature_name, feature_value, created_at FROM features WHERE 1=1"]
    params: List[Any] = []

    if symbol:
        query.append("AND symbol = ?")
        params.append(symbol)
    if timeframe:
        query.append("AND timeframe = ?")
        params.append(timeframe)
    if feature_name:
        query.append("AND feature_name = ?")
        params.append(feature_name)
    if bar_id is not None:
        query.append("AND bar_id = ?")
        params.append(bar_id)
    if start_time is not None:
        query.append("AND time >= ?")
        params.append(start_time)
    if end_time is not None:
        query.append("AND time <= ?")
        params.append(end_time)

    query.append("ORDER BY time ASC")
    sql_statement = " ".join(query)

    active_conn = conn or get_connection(db_path=db_path)
    try:
        if as_df:
            return pd.read_sql_query(sql_statement, active_conn, params=params)
        active_conn.row_factory = sqlite3.Row
        cursor = active_conn.cursor()
        cursor.execute(sql_statement, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if conn is None:
            active_conn.close()


def insert_prediction(
    record: Dict[str, Any],
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """
    Insert a model prediction record into the database.
    Supports ModelVersion, ProbabilityBuy, ProbabilitySell, ExpectedReturn,
    Confidence, and Timestamp fields.
    """
    sql = """
    INSERT INTO predictions (
        symbol, timeframe, timestamp, model_version,
        probability_buy, probability_sell, expected_return,
        confidence, prediction_type, prediction_value, probability, features_snapshot
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    ts = int(record.get("timestamp") or record.get("time") or 0)
    model_ver = record.get("model_version") or record.get("ModelVersion") or ""
    prob_buy = record.get("probability_buy") or record.get("ProbabilityBuy")
    prob_sell = record.get("probability_sell") or record.get("ProbabilitySell")
    exp_return = record.get("expected_return") or record.get("ExpectedReturn")
    conf = record.get("confidence") or record.get("Confidence")
    pred_type = record.get("prediction_type")
    pred_val = record.get("prediction_value")
    prob = record.get("probability") or prob_buy
    feat_snap = record.get("features_snapshot")

    params = (
        record.get("symbol"), record.get("timeframe"), ts, model_ver,
        float(prob_buy) if prob_buy is not None else None,
        float(prob_sell) if prob_sell is not None else None,
        float(exp_return) if exp_return is not None else None,
        float(conf) if conf is not None else None,
        pred_type,
        float(pred_val) if pred_val is not None else None,
        float(prob) if prob is not None else None,
        feat_snap
    )

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid

    with get_db_context(db_path=db_path) as context_conn:
        cursor = context_conn.cursor()
        cursor.execute(sql, params)
        return cursor.lastrowid


def get_predictions(
    symbol: Optional[str] = None,
    timeframe: Optional[str] = None,
    model_version: Optional[str] = None,
    limit: Optional[int] = None,
    as_df: bool = False,
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """Fetch model prediction records."""
    query = ["""
        SELECT
            id, symbol, timeframe, timestamp, timestamp as time,
            model_version, probability_buy, probability_sell,
            expected_return, confidence, prediction_type,
            prediction_value, probability, features_snapshot, created_at
        FROM predictions WHERE 1=1
    """]
    params: List[Any] = []

    if symbol:
        query.append("AND symbol = ?")
        params.append(symbol)
    if timeframe:
        query.append("AND timeframe = ?")
        params.append(timeframe)
    if model_version:
        query.append("AND model_version = ?")
        params.append(model_version)

    query.append("ORDER BY timestamp DESC")
    if limit is not None:
        query.append(f"LIMIT {int(limit)}")

    sql_statement = " ".join(query)
    active_conn = conn or get_connection(db_path=db_path)
    try:
        if as_df:
            return pd.read_sql_query(sql_statement, active_conn, params=params)
        active_conn.row_factory = sqlite3.Row
        cursor = active_conn.cursor()
        cursor.execute(sql_statement, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if conn is None:
            active_conn.close()


def insert_trade(
    trade_data: Dict[str, Any],
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """
    Insert a trade execution record into the database.
    Supports Entry, Exit, SL, TP, Lots, Profit, Commission, Swap, Reason, AI Version.
    """
    sql = """
    INSERT OR REPLACE INTO trades (
        ticket, symbol, trade_type, lots, volume,
        entry_price, entry_time, open_price, open_time,
        exit_price, exit_time, close_price, close_time,
        sl, tp, profit, commission, swap,
        reason, comment, ai_version, model_version, magic_number
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    lots = float(trade_data.get("lots") or trade_data.get("volume") or trade_data.get("Lots") or 0.0)
    entry_price = float(trade_data.get("entry_price") or trade_data.get("open_price") or trade_data.get("Entry") or 0.0)
    entry_time = int(trade_data.get("entry_time") or trade_data.get("open_time") or trade_data.get("time") or 0)
    exit_price = trade_data.get("exit_price") or trade_data.get("close_price") or trade_data.get("Exit")
    exit_time = trade_data.get("exit_time") or trade_data.get("close_time")
    reason = trade_data.get("reason") or trade_data.get("comment") or trade_data.get("Reason")
    ai_ver = trade_data.get("ai_version") or trade_data.get("model_version") or trade_data.get("AI Version")

    params = (
        int(trade_data["ticket"]),
        trade_data["symbol"],
        trade_data.get("trade_type", "BUY"),
        lots, lots,
        entry_price, entry_time, entry_price, entry_time,
        float(exit_price) if exit_price is not None else None,
        int(exit_time) if exit_time is not None else None,
        float(exit_price) if exit_price is not None else None,
        int(exit_time) if exit_time is not None else None,
        trade_data.get("sl") or trade_data.get("SL"),
        trade_data.get("tp") or trade_data.get("TP"),
        float(trade_data.get("profit") or trade_data.get("Profit") or 0.0),
        float(trade_data.get("commission") or trade_data.get("Commission") or 0.0),
        float(trade_data.get("swap") or trade_data.get("Swap") or 0.0),
        reason, reason,
        ai_ver, ai_ver,
        trade_data.get("magic_number")
    )

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid

    with get_db_context(db_path=db_path) as context_conn:
        cursor = context_conn.cursor()
        cursor.execute(sql, params)
        return cursor.lastrowid


def update_trade(
    ticket: int,
    close_time: Optional[int] = None,
    close_price: Optional[float] = None,
    profit: Optional[float] = None,
    exit_time: Optional[int] = None,
    exit_price: Optional[float] = None,
    commission: Optional[float] = None,
    swap: Optional[float] = None,
    reason: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> bool:
    """Update a trade with exit / close details."""
    final_exit_time = int(exit_time if exit_time is not None else (close_time or 0))
    final_exit_price = float(exit_price if exit_price is not None else (close_price or 0.0))
    final_profit = float(profit) if profit is not None else None

    sql = """
    UPDATE trades
    SET exit_time = ?, close_time = ?,
        exit_price = ?, close_price = ?,
        profit = COALESCE(?, profit),
        commission = COALESCE(?, commission),
        swap = COALESCE(?, swap),
        reason = COALESCE(?, reason),
        comment = COALESCE(?, comment)
    WHERE ticket = ?
    """
    params = (
        final_exit_time, final_exit_time,
        final_exit_price, final_exit_price,
        final_profit,
        commission,
        swap,
        reason, reason,
        int(ticket)
    )

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0

    with get_db_context(db_path=db_path) as context_conn:
        cursor = context_conn.cursor()
        cursor.execute(sql, params)
        return cursor.rowcount > 0


def get_trades(
    symbol: Optional[str] = None,
    open_only: bool = False,
    ai_version: Optional[str] = None,
    limit: Optional[int] = None,
    as_df: bool = False,
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """Retrieve trades with optional filtering."""
    sql = ["SELECT * FROM trades WHERE 1=1"]
    params: List[Any] = []

    if symbol:
        sql.append("AND symbol = ?")
        params.append(symbol)

    if open_only:
        sql.append("AND (exit_time IS NULL OR close_time IS NULL)")

    if ai_version:
        sql.append("AND (ai_version = ? OR model_version = ?)")
        params.extend([ai_version, ai_version])

    sql.append("ORDER BY entry_time DESC")

    if limit is not None:
        sql.append(f"LIMIT {int(limit)}")

    active_conn = conn or get_connection(db_path=db_path, row_factory=sqlite3.Row)
    try:
        if as_df:
            return pd.read_sql_query(" ".join(sql), active_conn, params=params)
        cursor = active_conn.cursor()
        cursor.execute(" ".join(sql), params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if conn is None:
            active_conn.close()


def insert_account_snapshot(
    snapshot: Dict[str, Any],
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """Insert an account equity/balance snapshot."""
    sql = """
    INSERT INTO account_history (
        timestamp, balance, equity, margin, free_margin, margin_level, profit, currency
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        int(snapshot["timestamp"]), float(snapshot["balance"]), float(snapshot["equity"]),
        snapshot.get("margin"), snapshot.get("free_margin"), snapshot.get("margin_level"),
        snapshot.get("profit"), snapshot.get("currency")
    )

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid

    with get_db_context(db_path=db_path) as context_conn:
        cursor = context_conn.cursor()
        cursor.execute(sql, params)
        return cursor.lastrowid


def get_latest_account_snapshot(
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> Optional[Dict[str, Any]]:
    """Retrieve the most recent account snapshot."""
    sql = "SELECT * FROM account_history ORDER BY timestamp DESC LIMIT 1"
    active_conn = conn or get_connection(db_path=db_path, row_factory=sqlite3.Row)
    try:
        cursor = active_conn.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        if conn is None:
            active_conn.close()


def get_account_history(
    limit: Optional[int] = None,
    as_df: bool = False,
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """Retrieve account history ordered by timestamp."""
    sql = ["SELECT * FROM account_history ORDER BY timestamp ASC"]
    if limit is not None:
        sql.append(f"LIMIT {int(limit)}")

    sql_statement = " ".join(sql)
    active_conn = conn or get_connection(db_path=db_path)
    try:
        if as_df:
            return pd.read_sql_query(sql_statement, active_conn)
        active_conn.row_factory = sqlite3.Row
        cursor = active_conn.cursor()
        cursor.execute(sql_statement)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if conn is None:
            active_conn.close()


def insert_model_version(
    model_data: Dict[str, Any],
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> str:
    """Insert or update a model version metadata entry."""
    sql = """
    INSERT OR REPLACE INTO model_versions (
        model_id, model_name, version, algorithm, hyperparameters,
        features_list, target_metric, metrics_json, model_path, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        model_data["model_id"], model_data["model_name"], model_data["version"],
        model_data.get("algorithm"), model_data.get("hyperparameters"),
        model_data.get("features_list"), model_data.get("target_metric"),
        model_data.get("metrics_json"), model_data.get("model_path"),
        model_data.get("status", "active")
    )

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return model_data["model_id"]

    with get_db_context(db_path=db_path) as context_conn:
        cursor = context_conn.cursor()
        cursor.execute(sql, params)
        return model_data["model_id"]


def get_model_versions(
    status: Optional[str] = None,
    limit: Optional[int] = None,
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """Retrieve model versions."""
    sql = ["SELECT * FROM model_versions WHERE 1=1"]
    params: List[Any] = []

    if status:
        sql.append("AND status = ?")
        params.append(status)

    sql.append("ORDER BY trained_date DESC")
    if limit is not None:
        sql.append(f"LIMIT {int(limit)}")

    active_conn = conn or get_connection(db_path=db_path, row_factory=sqlite3.Row)
    try:
        cursor = active_conn.cursor()
        cursor.execute(" ".join(sql), params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if conn is None:
            active_conn.close()


def insert_backtest_result(
    result_data: Dict[str, Any],
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """Insert a backtest result record."""
    sql = """
    INSERT INTO backtest_results (
        backtest_name, model_id, symbol, timeframe, start_date, end_date,
        initial_balance, final_balance, total_net_profit, profit_factor,
        sharpe_ratio, max_drawdown, max_drawdown_pct, total_trades, win_rate, parameters
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        result_data["backtest_name"], result_data.get("model_id"), result_data["symbol"],
        result_data["timeframe"], int(result_data["start_date"]), int(result_data["end_date"]),
        result_data.get("initial_balance"), result_data.get("final_balance"),
        result_data.get("total_net_profit"), result_data.get("profit_factor"),
        result_data.get("sharpe_ratio"), result_data.get("max_drawdown"),
        result_data.get("max_drawdown_pct"), result_data.get("total_trades"),
        result_data.get("win_rate"), result_data.get("parameters")
    )

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid

    with get_db_context(db_path=db_path) as context_conn:
        cursor = context_conn.cursor()
        cursor.execute(sql, params)
        return cursor.lastrowid


def get_backtest_results(
    symbol: Optional[str] = None,
    model_id: Optional[str] = None,
    limit: Optional[int] = None,
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """Retrieve backtest results."""
    sql = ["SELECT * FROM backtest_results WHERE 1=1"]
    params: List[Any] = []

    if symbol:
        sql.append("AND symbol = ?")
        params.append(symbol)
    if model_id:
        sql.append("AND model_id = ?")
        params.append(model_id)

    sql.append("ORDER BY created_at DESC")
    if limit is not None:
        sql.append(f"LIMIT {int(limit)}")

    active_conn = conn or get_connection(db_path=db_path, row_factory=sqlite3.Row)
    try:
        cursor = active_conn.cursor()
        cursor.execute(" ".join(sql), params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if conn is None:
            active_conn.close()
