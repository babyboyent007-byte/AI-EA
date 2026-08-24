import os
import sys
import sqlite3

def run_preflight():
    print("=== AI-EA LOCAL INTEGRITY CHECK ===")
    passed = True

    # Model Check
    print("\n[1/3] Verifying Ensemble Models...")
    required_models = ["lgbm_baseline.joblib", "xgb_bench.joblib", "rf_bench.joblib"]
    for m in required_models:
        path = os.path.join("models", m)
        if os.path.exists(path): print(f"  [OK] Found {m}")
        else:
            print(f"  [ERROR] Missing {m}")
            passed = False

    # Database Check
    print("\n[2/3] Verifying Market Database...")
    db_p = os.path.join("database", "market.db")
    if os.path.exists(db_p):
        try:
            conn = sqlite3.connect(db_p)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [t[0] for t in cursor.fetchall()]
            if "trades" in tables: print("  [OK] Table 'trades' verified.")
            else: print("  [ERROR] DB is corrupt or empty!"); passed = False
            conn.close()
        except Exception as e: print(f"  [ERROR] DB Error: {e}"); passed = False
    else:
        print("  [ERROR] market.db not found!")
        passed = False

    # Risk Circuit Breaker Check
    print("\n[3/3] Testing Logic Dependencies...")
    try:
        from risk_manager import RiskManager
        rm = RiskManager()
        print("  [OK] RiskManager module imported successfully.")
    except ImportError: print("  [ERROR] Local logic files missing!"); passed = False

    if passed: print("\nSUCCESS: Environment is intact for migration.")
    else: print("\nFAILURE: Correct the errors above before deploying.")

if __name__ == '__main__': run_preflight()