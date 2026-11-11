"""Session state and results models for Typr."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional

from typr.core.metrics import CharStats


class SessionState(Enum):
    """Lifecycle states of a typing session."""

    IDLE = auto()       # Uninitialized or reset
    READY = auto()      # Text loaded, waiting for first keypress
    RUNNING = auto()    # Keystrokes being actively registered, timer running
    PAUSED = auto()     # Timer paused (e.g. out of focus or user paused)
    COMPLETED = auto()  # Session finished naturally
    ABORTED = auto()    # Session aborted (e.g. failed in master/expert mode or user quit)


@dataclass(frozen=True)
class SessionConfig:
    """Configuration for an individual typing session."""

    mode: str = "words"              # "words", "time", "quotes", "code"
    amount: int = 25                 # Word count or time duration in seconds
    punctuation: bool = False        # Include punctuation
    numbers: bool = False            # Include numbers
    difficulty: str = "normal"       # "normal", "expert", "master"
    language: str = "english"        # English or programming language for code mode
    strict_space: bool = False       # Disallow space if current word has errors
    stop_on_error: str = "off"       # "off", "letter", "word"
    freedom_mode: bool = False       # Allow backspacing through previous words

    @property
    def label(self) -> str:
        """Human-readable description of current session config."""
        parts = [f"{self.mode} {self.amount}"]
        if self.mode in ("words", "time"):
            if self.punctuation:
                parts.append("punctuation")
            if self.numbers:
                parts.append("numbers")
        elif self.mode == "code":
            parts.append(self.language)
        if self.difficulty != "normal":
            parts.append(self.difficulty)
        return " • ".join(parts)


@dataclass
class TypingResult:
    """Detailed summary of a completed or aborted typing session."""

    net_wpm: float = 0.0
    raw_wpm: float = 0.0
    accuracy: float = 100.0
    consistency: float = 100.0
    duration: float = 0.0
    chars: CharStats = field(default_factory=CharStats)
    timeline: List[float] = field(default_factory=list)  # Speed samples per second
    failed_reason: Optional[str] = None
    config: SessionConfig = field(default_factory=SessionConfig)
    new_pb: bool = False
    personal_best: float = 0.0

    @property
    def is_success(self) -> bool:
        """True if session completed without being failed by difficulty constraints."""
        return self.failed_reason is None and self.duration > 0

