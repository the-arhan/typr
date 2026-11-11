"""Local SQLite session history and analytics for Typr.

Completely offline and private. Stores session logs, computes personal bests,
and aggregates performance trends without network requests.
"""

from __future__ import annotations

import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from typr.core.session import SessionConfig, TypingResult
from typr.storage.paths import get_data_dir, get_history_db_file


class HistoryManager:
    """Manages SQLite storage for typing session records."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path or get_history_db_file()
        self._init_db()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self.db_path))
        except (OSError, sqlite3.OperationalError):
            conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    mode TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    punctuation INTEGER NOT NULL,
                    numbers INTEGER NOT NULL,
                    language TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    net_wpm REAL NOT NULL,
                    raw_wpm REAL NOT NULL,
                    accuracy REAL NOT NULL,
                    consistency REAL NOT NULL,
                    duration REAL NOT NULL,
                    correct_chars INTEGER NOT NULL,
                    incorrect_chars INTEGER NOT NULL,
                    extra_chars INTEGER NOT NULL,
                    missed_chars INTEGER NOT NULL,
                    is_pb INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_time ON sessions(timestamp)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_sessions_mode ON sessions(mode, amount, punctuation, numbers)"
            )

    def get_personal_best(self, cfg: SessionConfig) -> float:
        """Retrieve highest Net WPM for the matching configuration."""
        query = """
            SELECT MAX(net_wpm) as pb FROM sessions
            WHERE mode = ? AND amount = ? AND punctuation = ? AND numbers = ? AND difficulty = ?
        """
        with self._connection() as conn:
            cur = conn.execute(
                query,
                (
                    cfg.mode,
                    cfg.amount,
                    int(cfg.punctuation),
                    int(cfg.numbers),
                    cfg.difficulty,
                ),
            )
            row = cur.fetchone()
            if row and row["pb"] is not None:
                return float(row["pb"])
        return 0.0

    def record_session(self, result: TypingResult) -> bool:
        """Record a completed session.

        Returns:
            True if this session established a new personal best, False otherwise.
        """
        if not result.is_success:
            return False

        old_pb = self.get_personal_best(result.config)
        is_new_pb = result.net_wpm > old_pb and result.net_wpm > 0.0
        result.new_pb = is_new_pb
        result.personal_best = max(old_pb, result.net_wpm)

        now = time.time()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO sessions (
                    timestamp, mode, amount, punctuation, numbers, language, difficulty,
                    net_wpm, raw_wpm, accuracy, consistency, duration,
                    correct_chars, incorrect_chars, extra_chars, missed_chars, is_pb
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    now,
                    result.config.mode,
                    result.config.amount,
                    int(result.config.punctuation),
                    int(result.config.numbers),
                    result.config.language,
                    result.config.difficulty,
                    result.net_wpm,
                    result.raw_wpm,
                    result.accuracy,
                    result.consistency,
                    result.duration,
                    result.chars.correct,
                    result.chars.incorrect,
                    result.chars.extra,
                    result.chars.missed,
                    int(is_new_pb),
                ),
            )
        return is_new_pb

    def get_summary_stats(self) -> Dict[str, Any]:
        """Compute aggregate statistics across all recorded sessions."""
        with self._connection() as conn:
            cur = conn.execute(
                """
                SELECT
                    COUNT(*) as total_tests,
                    SUM(duration) as total_time,
                    AVG(net_wpm) as avg_wpm,
                    MAX(net_wpm) as max_wpm,
                    AVG(accuracy) as avg_acc
                FROM sessions
                """
            )
            row = cur.fetchone()
            if not row or row["total_tests"] == 0:
                return {
                    "total_tests": 0,
                    "total_time_seconds": 0.0,
                    "avg_wpm": 0.0,
                    "max_wpm": 0.0,
                    "avg_accuracy": 0.0,
                }

            return {
                "total_tests": int(row["total_tests"]),
                "total_time_seconds": float(row["total_time"] or 0.0),
                "avg_wpm": float(row["avg_wpm"] or 0.0),
                "max_wpm": float(row["max_wpm"] or 0.0),
                "avg_accuracy": float(row["avg_acc"] or 0.0),
            }

    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent sessions in descending chronological order."""
        with self._connection() as conn:
            cur = conn.execute(
                """
                SELECT timestamp, mode, amount, punctuation, numbers, language, difficulty,
                       net_wpm, raw_wpm, accuracy, consistency, duration, is_pb
                FROM sessions
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cur.fetchall()]

    def clear_history(self) -> None:
        """Clear all historical session logs."""
        with self._connection() as conn:
            conn.execute("DELETE FROM sessions")
