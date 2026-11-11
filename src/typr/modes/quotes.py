"""Quotes typing mode."""

from __future__ import annotations

import random
from typr.core.engine import TypingEngine
from typr.core.session import SessionConfig
from typr.core.text_source import load_quotes
from typr.modes.base import BaseMode
from typr.storage.config import AppConfig


class QuotesMode(BaseMode):
    """Historical and literature quote typing session."""

    def __init__(self) -> None:
        self.current_quote_source: str = ""

    @property
    def name(self) -> str:
        return "quotes"

    def build_engine(self, config: AppConfig) -> TypingEngine:
        quotes = load_quotes()
        quote = random.choice(quotes)
        self.current_quote_source = quote.get("source", "Unknown")
        words = quote["text"].split()

        session_cfg = SessionConfig(
            mode="quotes",
            amount=len(words),
            difficulty=config.difficulty,
            language=config.language,
        )
        return TypingEngine(session_cfg, words)

    def get_summary_label(self, config: AppConfig) -> str:
        label = "quote"
        if self.current_quote_source:
            label += f" ({self.current_quote_source})"
        return label

