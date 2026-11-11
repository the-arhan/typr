"""Typing modes registry and implementations."""

from typr.modes.base import BaseMode
from typr.modes.code import CodeMode
from typr.modes.quotes import QuotesMode
from typr.modes.time import TimeMode
from typr.modes.words import WordsMode
from typr.storage.config import AppConfig


def get_mode_handler(mode_name: str) -> BaseMode:
    """Factory to retrieve a mode handler by name."""
    handlers = {
        "words": WordsMode,
        "time": TimeMode,
        "quotes": QuotesMode,
        "code": CodeMode,
    }
    handler_cls = handlers.get(mode_name, WordsMode)
    return handler_cls()


__all__ = [
    "BaseMode",
    "WordsMode",
    "TimeMode",
    "QuotesMode",
    "CodeMode",
    "get_mode_handler",
]

