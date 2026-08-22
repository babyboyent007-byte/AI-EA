"""Unit tests for database module."""

import tempfile
import unittest
from pathlib import Path
import pandas as pd

from database import (
    ALL_TABLES,
    DatabaseManager,
    create_tables,
    get_available_symbols,
    get_candle_count,
    get_candles,
    get_connection,
    get_db_context,
    get_features,
    get_indicators,
    get_predictions,
    get_trades,
    insert_account_snapshot,
    insert_backtest_result,
    insert_candles,
    insert_features,
    insert_indicators,
    insert_model_version,
    insert_prediction,
    insert_trade,
    update_trade,
)


class TestDatabaseModule(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_market.db"
        self.db_manager = DatabaseManager(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_schema_creation(self):
        with get_db_context(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
            self.assertEqual(len(tables), len(ALL_TABLES))

    def test_candle_operations(self):
        df_candles = pd.DataFrame([
            {
                "symbol": "EURUSD",
                "timeframe": "M5",
                "time": 1700000000 + i * 300,
                "open": 1.0800 + i * 0.0001,
                "high": 1.0810 + i * 0.0001,
                "low": 1.0790 + i * 0.0001,
                "close": 1.0805 + i * 0.0001,
                "tick_volume": 100 + i,
                "spread": 10,
                "real_volume": 0
            }
            for i in range(5)
        ])

        inserted = insert_candles(df_candles, db_path=self.db_path)
        self.assertEqual(inserted, 5)

        count = get_candle_count("EURUSD", "M5", db_path=self.db_path)
        self.assertEqual(count, 5)

        candles_df = get_candles("EURUSD", "M5", as_df=True, db_path=self.db_path)
        self.assertEqual(len(candles_df), 5)
        self.assertEqual(candles_df.iloc[0]["symbol"], "EURUSD")

        symbols = get_available_symbols(db_path=self.db_path)
        self.assertEqual(len(symbols), 1)
        self.assertEqual(symbols[0]["symbol"], "EURUSD")
        self.assertEqual(symbols[0]["total_bars"], 5)

    def test_indicators_and_features(self):
        indicators = [
            {"symbol": "EURUSD", "timeframe": "M5", "time": 1700000000, "indicator_name": "EMA20", "value": 1.0850, "params": '{"period": 20}'},
            {"symbol": "EURUSD", "timeframe": "M5", "time": 1700000000, "indicator_name": "RSI14", "value": 55.4, "params": '{"period": 14}'},
            {"symbol": "EURUSD", "timeframe": "M5", "time": 1700000000, "indicator_name": "ATR14", "value": 0.0012, "params": '{"period": 14}'},
            {"symbol": "EURUSD", "timeframe": "M5", "time": 1700000000, "indicator_name": "MACD", "value": 0.0004, "params": '{"fast": 12, "slow": 26, "signal": 9}'}
        ]
        inserted_ind = insert_indicators(indicators, db_path=self.db_path)
        self.assertEqual(inserted_ind, 4)

        # Test features key-value structure (BarID, FeatureName, FeatureValue)
        features = [
            {"BarID": 1, "symbol": "EURUSD", "timeframe": "M5", "time": 1700000000, "FeatureName": "rsi_norm", "FeatureValue": 0.554},
            {"BarID": 1, "symbol": "EURUSD", "timeframe": "M5", "time": 1700000000, "FeatureName": "ema_ratio", "FeatureValue": 1.002},
            {"BarID": 1, "symbol": "EURUSD", "timeframe": "M5", "time": 1700000000, "FeatureName": "volatility_zscore", "FeatureValue": -0.32}
        ]
        inserted_feat = insert_features(features, db_path=self.db_path)
        self.assertEqual(inserted_feat, 3)

        feat_records = get_features(bar_id=1, db_path=self.db_path, as_df=False)
        self.assertEqual(len(feat_records), 3)

    def test_predictions_schema(self):
        prediction = {
            "symbol": "EURUSD",
            "timeframe": "M5",
            "Timestamp": 1700000000,
            "ModelVersion": "v1.0.0_xgb",
            "ProbabilityBuy": 0.75,
            "ProbabilitySell": 0.25,
            "ExpectedReturn": 0.0015,
            "Confidence": 0.88
        }
        pred_id = insert_prediction(prediction, db_path=self.db_path)
        self.assertIsNotNone(pred_id)

        preds = get_predictions(symbol="EURUSD", model_version="v1.0.0_xgb", db_path=self.db_path, as_df=False)
        self.assertEqual(len(preds), 1)
        self.assertEqual(preds[0]["model_version"], "v1.0.0_xgb")
        self.assertAlmostEqual(preds[0]["probability_buy"], 0.75)
        self.assertAlmostEqual(preds[0]["probability_sell"], 0.25)
        self.assertAlmostEqual(preds[0]["expected_return"], 0.0015)
        self.assertAlmostEqual(preds[0]["confidence"], 0.88)

    def test_trade_lifecycle(self):
        trade = {
            "ticket": 123456,
            "symbol": "EURUSD",
            "trade_type": "BUY",
            "Lots": 0.1,
            "Entry": 1.0850,
            "entry_time": 1700000000,
            "SL": 1.0800,
            "TP": 1.0950,
            "Commission": -2.0,
            "Swap": -0.5,
            "Reason": "AI Signal Buy Breakout",
            "AI Version": "v1.0.0_xgb",
            "magic_number": 999
        }
        insert_trade(trade, db_path=self.db_path)
        trades = get_trades(symbol="EURUSD", open_only=True, db_path=self.db_path)
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]["ticket"], 123456)
        self.assertEqual(trades[0]["lots"], 0.1)
        self.assertEqual(trades[0]["reason"], "AI Signal Buy Breakout")
        self.assertEqual(trades[0]["ai_version"], "v1.0.0_xgb")

        # Update / close trade with Exit, Profit
        updated = update_trade(
            ticket=123456,
            exit_time=1700000300,
            exit_price=1.0900,
            profit=50.0,
            reason="TP Hit",
            db_path=self.db_path
        )
        self.assertTrue(updated)

        open_trades = get_trades(symbol="EURUSD", open_only=True, db_path=self.db_path)
        self.assertEqual(len(open_trades), 0)

        all_trades = get_trades(symbol="EURUSD", open_only=False, db_path=self.db_path)
        self.assertEqual(len(all_trades), 1)
        self.assertEqual(all_trades[0]["profit"], 50.0)
        self.assertEqual(all_trades[0]["exit_price"], 1.0900)


if __name__ == "__main__":
    unittest.main()
