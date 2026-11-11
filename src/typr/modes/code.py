"""Programming and code snippet typing mode."""

from __future__ import annotations

import random
from typr.core.engine import TypingEngine
from typr.core.session import SessionConfig
from typr.core.text_source import load_code_snippets
from typr.modes.base import BaseMode
from typr.storage.config import AppConfig


class CodeMode(BaseMode):
    """Programming syntax snippet typing session."""

    def __init__(self) -> None:
        self.language: str = "python"

    @property
    def name(self) -> str:
        return "code"

    def build_engine(self, config: AppConfig) -> TypingEngine:
        self.language = config.code_language
        snippets = load_code_snippets(self.language)
        snippet = random.choice(snippets)
        words = snippet.split()

        session_cfg = SessionConfig(
            mode="code",
            amount=len(words),
            difficulty=config.difficulty,
            language=self.language,
        )
        return TypingEngine(session_cfg, words)

    def get_summary_label(self, config: AppConfig) -> str:
        return f"code • {self.language}"

