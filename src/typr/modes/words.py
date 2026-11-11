"""Words typing mode."""

from __future__ import annotations

from typr.core.engine import TypingEngine
from typr.core.session import SessionConfig
from typr.core.text_source import TextSource
from typr.modes.base import BaseMode
from typr.storage.config import AppConfig


class WordsMode(BaseMode):
    """Word count constrained typing session."""

    @property
    def name(self) -> str:
        return "words"

    def build_engine(self, config: AppConfig) -> TypingEngine:
        source = TextSource(
            wordlist_name=config.language,
            punctuation=config.punctuation,
            numbers=config.numbers,
        )
        words = source.generate_words(config.words)
        session_cfg = SessionConfig(
            mode="words",
            amount=config.words,
            punctuation=config.punctuation,
            numbers=config.numbers,
            difficulty=config.difficulty,
            language=config.language,
        )
        return TypingEngine(session_cfg, words)

    def get_summary_label(self, config: AppConfig) -> str:
        parts = [f"words {config.words}"]
        if config.punctuation:
            parts.append("punctuation")
        if config.numbers:
            parts.append("numbers")
        if config.difficulty != "normal":
            parts.append(config.difficulty)
        return " • ".join(parts)

