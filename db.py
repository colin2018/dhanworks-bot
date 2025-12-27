"""
Database resource management module.

This module provides context managers and utilities for safe database operations
with proper resource handling, connection pooling, and error management.
"""

import sqlite3
import logging
import os
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Generator, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Configuration for database connections and operations."""

    def __init__(
        self,
        db_path: str = "dhanworks.db",
        timeout: float = 5.0,
        check_same_thread: bool = False,
        isolation_level: Optional[str] = None,
    ):
        """
        Initialize database configuration.

        Args:
            db_path: Path to the SQLite database file.
            timeout: Timeout for database locks in seconds.
            check_same_thread: Whether to enforce same-thread access.
            isolation_level: Transaction isolation level (None for autocommit).
        """
        self.db_path = db_path
        self.timeout = timeout
        self.check_same_thread = check_same_thread
        self.isolation_level = isolation_level

    def ensure_db_directory(self) -> None:
        """Create database directory if it doesn't exist."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            Path(db_dir).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created database directory: {db_dir}")


class DatabaseConnection:
    """Manages a single database connection with safe resource handling."""

    def __init__(self, config: DatabaseConfig):
        """
        Initialize database connection manager.

        Args:
            config: DatabaseConfig instance for connection parameters.
        """
        self.config = config
        self.connection: Optional[sqlite3.Connection] = None

    def __enter__(self) -> sqlite3.Connection:
        """Enter context manager and establish connection."""
        try:
            self.config.ensure_db_directory()
            self.connection = sqlite3.connect(
                self.config.db_path,
                timeout=self.config.timeout,
                check_same_thread=self.config.check_same_thread,
            )
            if self.config.isolation_level is not None:
                self.connection.isolation_level = self.config.isolation_level
            self.connection.row_factory = sqlite3.Row
            logger.debug(f"Database connection established: {self.config.db_path}")
            return self.connection
        except sqlite3.Error as e:
            logger.error(f"Failed to establish database connection: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager and close connection."""
        if self.connection:
            try:
                if exc_type is None:
                    self.connection.commit()
                    logger.debug("Database transaction committed")
                else:
                    self.connection.rollback()
                    logger.warning(f"Database transaction rolled back due to: {exc_type.__name__}")
            except sqlite3.Error as e:
                logger.error(f"Error during transaction handling: {e}")
            finally:
                self.connection.close()
                logger.debug("Database connection closed")


class DatabaseManager:
    """High-level database manager with safe resource handling."""

    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize database manager.

        Args:
            config: DatabaseConfig instance. Uses defaults if None.
        """
        self.config = config or DatabaseConfig()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Get a database connection as a context manager.

        Yields:
            sqlite3.Connection: An active database connection.

        Example:
            with manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
        """
        db_conn = DatabaseConnection(self.config)
        with db_conn as conn:
            yield conn

    @contextmanager
    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """
        Get a database cursor as a context manager.

        Yields:
            sqlite3.Cursor: An active database cursor.

        Example:
            with manager.get_cursor() as cursor:
                cursor.execute("INSERT INTO users VALUES (?, ?)", (1, "John"))
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()

    def execute(
        self,
        query: str,
        params: Optional[Tuple[Any, ...]] = None,
        fetch: str = "none",
    ) -> Any:
        """
        Execute a database query with automatic resource management.

        Args:
            query: SQL query to execute.
            params: Query parameters for parameterized queries.
            fetch: Result fetching mode ('none', 'one', 'all').

        Returns:
            Query results based on fetch mode, or None if fetch='none'.

        Raises:
            ValueError: If fetch mode is invalid.
        """
        if fetch not in ("none", "one", "all"):
            raise ValueError(f"Invalid fetch mode: {fetch}")

        with self.get_cursor() as cursor:
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                if fetch == "one":
                    return cursor.fetchone()
                elif fetch == "all":
                    return cursor.fetchall()
                else:
                    return None
            except sqlite3.Error as e:
                logger.error(f"Database query error: {e}\nQuery: {query}")
                raise

    def execute_many(
        self,
        query: str,
        params_list: List[Tuple[Any, ...]],
    ) -> int:
        """
        Execute multiple queries with the same structure.

        Args:
            query: SQL query to execute.
            params_list: List of parameter tuples for each query execution.

        Returns:
            Number of rows affected.
        """
        with self.get_cursor() as cursor:
            try:
                cursor.executemany(query, params_list)
                return cursor.rowcount
            except sqlite3.Error as e:
                logger.error(f"Database batch query error: {e}\nQuery: {query}")
                raise

    def initialize_schema(self, schema_sql: str) -> None:
        """
        Initialize database schema from SQL statements.

        Args:
            schema_sql: SQL statements to create tables and indexes.
        """
        with self.get_connection() as conn:
            try:
                conn.executescript(schema_sql)
                logger.info("Database schema initialized successfully")
            except sqlite3.Error as e:
                logger.error(f"Failed to initialize database schema: {e}")
                raise

    def backup(self, backup_path: str) -> None:
        """
        Create a backup of the database.

        Args:
            backup_path: Path where the backup should be created.
        """
        try:
            with self.get_connection() as source:
                backup_conn = sqlite3.connect(backup_path)
                source.backup(backup_conn)
                backup_conn.close()
                logger.info(f"Database backed up to: {backup_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to backup database: {e}")
            raise

    def close(self) -> None:
        """Close all connections and cleanup resources."""
        # SQLite handles connection cleanup automatically
        logger.info("Database manager closed")


class TransactionManager:
    """Manages database transactions with context managers."""

    def __init__(self, manager: DatabaseManager):
        """
        Initialize transaction manager.

        Args:
            manager: DatabaseManager instance to use for transactions.
        """
        self.manager = manager

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Cursor, None, None]:
        """
        Create a transaction context manager.

        Yields:
            sqlite3.Cursor: A cursor for executing transaction queries.

        Example:
            with tx_manager.transaction() as cursor:
                cursor.execute("INSERT INTO users VALUES (?, ?)", (1, "John"))
                cursor.execute("INSERT INTO logs VALUES (?, ?)", ("user_created", "success"))
        """
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("BEGIN")
                yield cursor
                conn.commit()
                logger.debug("Transaction committed successfully")
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction rolled back due to error: {e}")
                raise
            finally:
                cursor.close()

    @contextmanager
    def savepoint(self, name: str = "sp") -> Generator[sqlite3.Cursor, None, None]:
        """
        Create a savepoint within a transaction.

        Args:
            name: Name of the savepoint.

        Yields:
            sqlite3.Cursor: A cursor for executing queries within the savepoint.
        """
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"SAVEPOINT {name}")
                yield cursor
                cursor.execute(f"RELEASE SAVEPOINT {name}")
                logger.debug(f"Savepoint '{name}' released successfully")
            except Exception as e:
                cursor.execute(f"ROLLBACK TO SAVEPOINT {name}")
                logger.error(f"Savepoint '{name}' rolled back due to error: {e}")
                raise
            finally:
                cursor.close()


class QueryBuilder:
    """Helper class for building common database queries safely."""

    @staticmethod
    def select(
        table: str,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, List[Any]]:
        """
        Build a SELECT query.

        Args:
            table: Table name.
            columns: Columns to select (None for all).
            where: Dictionary of WHERE conditions.

        Returns:
            Tuple of (query_string, params_list).
        """
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table}"
        params = []

        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        return query, params

    @staticmethod
    def insert(
        table: str,
        data: Dict[str, Any],
    ) -> Tuple[str, List[Any]]:
        """
        Build an INSERT query.

        Args:
            table: Table name.
            data: Dictionary of column:value pairs.

        Returns:
            Tuple of (query_string, params_list).
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        params = list(data.values())

        return query, params

    @staticmethod
    def update(
        table: str,
        data: Dict[str, Any],
        where: Dict[str, Any],
    ) -> Tuple[str, List[Any]]:
        """
        Build an UPDATE query.

        Args:
            table: Table name.
            data: Dictionary of column:value pairs to update.
            where: Dictionary of WHERE conditions.

        Returns:
            Tuple of (query_string, params_list).
        """
        set_clause = ", ".join(f"{key} = ?" for key in data.keys())
        query = f"UPDATE {table} SET {set_clause}"
        params = list(data.values())

        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        return query, params

    @staticmethod
    def delete(
        table: str,
        where: Dict[str, Any],
    ) -> Tuple[str, List[Any]]:
        """
        Build a DELETE query.

        Args:
            table: Table name.
            where: Dictionary of WHERE conditions.

        Returns:
            Tuple of (query_string, params_list).
        """
        query = f"DELETE FROM {table}"
        params = []

        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        return query, params


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def init_database(config: Optional[DatabaseConfig] = None) -> DatabaseManager:
    """
    Initialize the global database manager.

    Args:
        config: DatabaseConfig instance. Uses defaults if None.

    Returns:
        The initialized DatabaseManager instance.
    """
    global _db_manager
    _db_manager = DatabaseManager(config)
    logger.info("Database manager initialized")
    return _db_manager


def get_database() -> DatabaseManager:
    """
    Get the global database manager instance.

    Returns:
        The DatabaseManager instance.

    Raises:
        RuntimeError: If database manager hasn't been initialized.
    """
    if _db_manager is None:
        raise RuntimeError("Database manager not initialized. Call init_database() first.")
    return _db_manager
