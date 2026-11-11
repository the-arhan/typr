"""Base contract for typing modes in Typr."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple

from typr.core.engine import TypingEngine
from typr.storage.config import AppConfig


class BaseMode(ABC):
    """Abstract base class for all typing modes."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the mode (e.g. 'words', 'time', 'quotes', 'code')."""
        pass

    @abstractmethod
    def build_engine(self, config: AppConfig) -> TypingEngine:
        """Construct and configure a TypingEngine instance for this mode."""
        pass

    @abstractmethod
    def get_summary_label(self, config: AppConfig) -> str:
        """Short label describing current mode settings."""
        pass

