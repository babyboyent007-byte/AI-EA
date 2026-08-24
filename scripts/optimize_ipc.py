import sqlite3
import os

DB_PATH = os.path.join("database", "market.db")

def apply_ipc_optimizations():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database {DB_PATH} not found.")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        # WAL mode allows concurrent readers and one writer without blocking
        conn.execute("PRAGMA journal_mode=WAL;")
        # Synchronous NORMAL is faster and sufficient for non-critical logging during competitions
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.close()
        print("[SUCCESS] SQLite IPC optimized with WAL mode and NORMAL synchronicity.")
    except Exception as e:
        print(f"[ERROR] Failed to optimize IPC: {e}")

if __name__ == '__main__':
    apply_ipc_optimizations()