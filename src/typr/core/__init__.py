"""Core typing engine, metrics, and session models for Typr."""

from typr.core.engine import TypingEngine
from typr.core.metrics import (
    CharStats,
    calculate_accuracy,
    calculate_consistency,
    calculate_wpm,
)
from typr.core.session import SessionConfig, SessionState, TypingResult
from typr.core.text_source import TextSource, load_code_snippets, load_quotes
from typr.core.timer import SessionTimer

__all__ = [
    "TypingEngine",
    "SessionTimer",
    "SessionConfig",
    "SessionState",
    "TypingResult",
    "CharStats",
    "calculate_wpm",
    "calculate_accuracy",
    "calculate_consistency",
    "TextSource",
    "load_quotes",
    "load_code_snippets",
]

