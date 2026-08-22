"""
Database connection and lifecycle management for the AI EA system.
Provides connection factories, context managers, and schema initialization.
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Union

from .schema import ALL_TABLES, INDICES

# Default database location (project root or fallback to data directory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "market_data.db"
LEGACY_DB_PATH = PROJECT_ROOT / "data" / "market_data.db"


def resolve_db_path(db_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Resolve the database file path.
    Prioritizes explicit argument, environment variable, existing data location, and project root.
    """
    if db_path is not None:
        return Path(db_path)

    env_path = os.environ.get("AI_EA_DB_PATH")
    if env_path:
        return Path(env_path)

    # Check legacy data directory if populated with market data
    if LEGACY_DB_PATH.exists() and (not DEFAULT_DB_PATH.exists() or LEGACY_DB_PATH.stat().st_size > DEFAULT_DB_PATH.stat().st_size):
        return LEGACY_DB_PATH
    if DEFAULT_DB_PATH.exists():
        return DEFAULT_DB_PATH

    return DEFAULT_DB_PATH


def get_connection(
    db_path: Optional[Union[str, Path]] = None,
    timeout: float = 30.0,
    check_same_thread: bool = False,
    row_factory: Optional[type] = None
) -> sqlite3.Connection:
    """
    Create and return a new SQLite database connection.
    
    Args:
        db_path: Path to the SQLite database file.
        timeout: SQLite lock timeout in seconds.
        check_same_thread: SQLite threading constraint check.
        row_factory: Optional row factory (e.g., sqlite3.Row).
        
    Returns:
        sqlite3.Connection instance.
    """
    target_path = resolve_db_path(db_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        str(target_path),
        timeout=timeout,
        check_same_thread=check_same_thread
    )
    if row_factory:
        conn.row_factory = row_factory

    # Enable foreign keys and WAL mode for better concurrency
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")

    return conn


@contextmanager
def get_db_context(
    db_path: Optional[Union[str, Path]] = None,
    row_factory: Optional[type] = None
) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager providing a managed database connection with automatic commit/rollback.
    """
    conn = get_connection(db_path=db_path, row_factory=row_factory)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_tables(conn: Optional[sqlite3.Connection] = None, db_path: Optional[Union[str, Path]] = None) -> None:
    """
    Execute DDL statements to create all tables and indices if they do not already exist.
    """
    should_close = False
    if conn is None:
        conn = get_connection(db_path=db_path)
        should_close = True

    try:
        cursor = conn.cursor()
        for statement in ALL_TABLES:
            cursor.execute(statement)

        for index_statement in INDICES:
            cursor.execute(index_statement)

        conn.commit()
    finally:
        if should_close:
            conn.close()


def init_database(db_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Initialize database file and create all schemas.
    
    Returns:
        Path to the initialized database file.
    """
    target_path = resolve_db_path(db_path)
    create_tables(db_path=target_path)
    return target_path


class DatabaseManager:
    """Convenience class to manage database interactions."""

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.db_path = resolve_db_path(db_path)
        self.init_db()

    def init_db(self) -> None:
        create_tables(db_path=self.db_path)

    def get_connection(self, row_factory: Optional[type] = None) -> sqlite3.Connection:
        return get_connection(db_path=self.db_path, row_factory=row_factory)

    @contextmanager
    def context(self, row_factory: Optional[type] = None) -> Generator[sqlite3.Connection, None, None]:
        with get_db_context(db_path=self.db_path, row_factory=row_factory) as conn:
            yield conn
