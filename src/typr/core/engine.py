"""Core typing engine for Typr.

Completely decoupled from terminal/curses rendering.
Implements the session state machine, deterministic input evaluation,
metrics tracking, and difficulty enforcement.
"""

from __future__ import annotations

import time
from typing import List, Optional

from typr.core.metrics import (
    CharStats,
    calculate_accuracy,
    calculate_consistency,
    calculate_wpm,
)
from typr.core.session import SessionConfig, SessionState, TypingResult
from typr.core.timer import SessionTimer


class TypingEngine:
    """Manages the state, input, and metrics of a typing session."""

    def __init__(self, config: SessionConfig, target_words: List[str]) -> None:
        self.config = config
        self.target_words = list(target_words)
        self.typed_words: List[str] = [""]
        self.current_idx: int = 0

        self.state: SessionState = SessionState.READY
        self.timer = SessionTimer()

        self.total_keystrokes: int = 0
        self.correct_keystrokes: int = 0
        self.fail_reason: Optional[str] = None

        # Per-second timeline records for graphing
        self._timeline_times: List[float] = []
        self._timeline_raw: List[int] = []
        self._timeline_correct: List[int] = []

        # Burst tracking
        self._last_word_time: Optional[float] = None
        self.current_burst: Optional[float] = None
        self._bursts: List[float] = []

        self.result: Optional[TypingResult] = None

    def extend_words(self, words: List[str]) -> None:
        """Add more words to the session buffer (used dynamically in time mode)."""
        self.target_words.extend(words)

    def _start_if_needed(self) -> None:
        if self.state == SessionState.READY:
            self.state = SessionState.RUNNING
            self.timer.start()
            self._last_word_time = time.monotonic()

    # ----------------------------------------------------------------------- #
    # Keystroke Processing
    # ----------------------------------------------------------------------- #
    def press_key(self, char: str) -> bool:
        """Process a character keystroke.

        Returns:
            True if key was accepted/processed, False otherwise.
        """
        if self.state in (SessionState.COMPLETED, SessionState.ABORTED):
            return False

        if char == " ":
            return self.press_space()

        self._start_if_needed()

        if self.current_idx >= len(self.target_words):
            return False

        target_word = self.target_words[self.current_idx]
        cur_typed = self.typed_words[self.current_idx]

        # Maximum extra characters allowed beyond target word length
        if len(cur_typed) >= len(target_word) + 20:
            return False

        char_idx = len(cur_typed)
        is_correct = char_idx < len(target_word) and target_word[char_idx] == char

        self.total_keystrokes += 1
        if is_correct:
            self.correct_keystrokes += 1
        else:
            if self.config.difficulty == "master":
                self.typed_words[self.current_idx] = cur_typed + char
                self.fail("master difficulty: incorrect character")
                return True
            if self.config.stop_on_error == "letter":
                # Block progress until corrected
                return False

        self.typed_words[self.current_idx] = cur_typed + char

        # Check completion condition for words mode on final word
        if self.config.mode in ("words", "quotes", "code") and self.current_idx == len(self.target_words) - 1:
            if self.typed_words[self.current_idx] == target_word:
                self.finish()

        return True

    def press_space(self) -> bool:
        """Process space bar input to submit the current word."""
        if self.state in (SessionState.COMPLETED, SessionState.ABORTED):
            return False

        cur_typed = self.typed_words[self.current_idx]
        # Ignore leading space on an empty word
        if not cur_typed:
            return False

        self._start_if_needed()

        target_word = self.target_words[self.current_idx]
        is_word_correct = cur_typed == target_word

        self.total_keystrokes += 1
        if is_word_correct:
            self.correct_keystrokes += 1
        else:
            if self.config.difficulty in ("expert", "master"):
                self.fail(f"{self.config.difficulty} difficulty: submitted incorrect word")
                return True
            if self.config.strict_space or self.config.stop_on_error == "word":
                return False

        # Record burst typing speed for the submitted word
        now = time.monotonic()
        if self._last_word_time is not None:
            dt = now - self._last_word_time
            if dt > 0.001:
                burst = (len(cur_typed) + 1) / 5.0 * 60.0 / dt
                self.current_burst = burst
                self._bursts.append(burst)
        self._last_word_time = now

        # Final word completed
        if self.current_idx == len(self.target_words) - 1:
            self.finish()
            return True

        self.current_idx += 1
        while len(self.typed_words) <= self.current_idx:
            self.typed_words.append("")

        return True

    def can_backspace_to_previous_word(self) -> bool:
        """Check if backspace is allowed to jump to the preceding word."""
        if self.current_idx == 0:
            return False
        if self.config.freedom_mode:
            return True
        # Allow returning only if the previous word contained an error
        prev_idx = self.current_idx - 1
        return self.typed_words[prev_idx] != self.target_words[prev_idx]

    def press_backspace(self) -> bool:
        """Delete the most recent character."""
        if self.state in (SessionState.COMPLETED, SessionState.ABORTED):
            return False

        cur_typed = self.typed_words[self.current_idx]
        if cur_typed:
            self.typed_words[self.current_idx] = cur_typed[:-1]
            return True
        elif self.can_backspace_to_previous_word():
            self.current_idx -= 1
            return True
        return False

    def delete_word(self) -> bool:
        """Delete the entire current word or jump back to clear previous."""
        if self.state in (SessionState.COMPLETED, SessionState.ABORTED):
            return False

        cur_typed = self.typed_words[self.current_idx]
        if cur_typed:
            self.typed_words[self.current_idx] = ""
            return True
        elif self.can_backspace_to_previous_word():
            self.current_idx -= 1
            self.typed_words[self.current_idx] = ""
            return True
        return False

    # ----------------------------------------------------------------------- #
    # Lifecycle & Timers
    # ----------------------------------------------------------------------- #
    def tick(self) -> None:
        """Periodic clock tick for time mode checks and telemetry sampling."""
        if self.state != SessionState.RUNNING:
            return

        elapsed = self.timer.elapsed()
        target_second = int(elapsed)

        # Snapshot per-second stats for timeline graphing
        if self.config.mode == "time":
            target_second = min(target_second, self.config.amount)

        while len(self._timeline_times) < target_second:
            sec = len(self._timeline_times) + 1
            self._timeline_times.append(float(sec))
            self._timeline_raw.append(self.get_total_typed_chars())
            self._timeline_correct.append(self.get_correct_chars(strict=False))

        # Check time expiration
        if self.config.mode == "time" and elapsed >= self.config.amount:
            self.finish()

    def finish(self) -> None:
        """Terminate the session and compute final metrics."""
        if self.result is not None:
            return

        duration = self.timer.stop()
        if self.fail_reason:
            self.state = SessionState.ABORTED
        else:
            self.state = SessionState.COMPLETED

        if self.config.mode == "time" and not self.fail_reason:
            duration = float(self.config.amount)

        duration = max(0.01, duration)
        chars = self.get_char_stats()

        net_wpm = calculate_wpm(self.get_correct_chars(strict=True), duration)
        raw_wpm = calculate_wpm(self.get_total_typed_chars(), duration)
        acc = calculate_accuracy(self.correct_keystrokes, self.total_keystrokes)
        cons = calculate_consistency(self._bursts)

        # Build timeline WPM progression
        timeline_wpm: List[float] = []
        for t, ok in zip(self._timeline_times, self._timeline_correct):
            if t > 0:
                timeline_wpm.append(calculate_wpm(ok, t))

        self.result = TypingResult(
            net_wpm=net_wpm,
            raw_wpm=raw_wpm,
            accuracy=acc,
            consistency=cons,
            duration=duration,
            chars=chars,
            timeline=timeline_wpm,
            failed_reason=self.fail_reason,
            config=self.config,
        )

    def fail(self, reason: str) -> None:
        """Abort the session due to a rule failure."""
        self.fail_reason = reason
        self.state = SessionState.ABORTED
        self.finish()

    # ----------------------------------------------------------------------- #
    # Character & Stats Queries
    # ----------------------------------------------------------------------- #
    def get_total_typed_chars(self) -> int:
        """Return total character count typed so far, including submitted spaces."""
        total = 0
        for i in range(self.current_idx):
            total += len(self.typed_words[i]) + 1  # +1 for space
        if self.current_idx < len(self.typed_words):
            total += len(self.typed_words[self.current_idx])
        return total

    def get_correct_chars(self, strict: bool = False) -> int:
        """Return count of correctly typed characters."""
        correct = 0
        for i in range(self.current_idx):
            if i < len(self.target_words) and self.typed_words[i] == self.target_words[i]:
                correct += len(self.target_words[i]) + 1

        if self.current_idx < len(self.target_words) and self.current_idx < len(self.typed_words):
            cur_typed = self.typed_words[self.current_idx]
            cur_target = self.target_words[self.current_idx]
            if (cur_typed == cur_target) if strict else cur_target.startswith(cur_typed):
                correct += len(cur_typed)

        return correct

    def get_char_stats(self) -> CharStats:
        """Return detailed breakdown of character outcomes."""
        correct = 0
        incorrect = 0
        extra = 0
        missed = 0

        for idx in range(min(self.current_idx + 1, len(self.target_words))):
            target = self.target_words[idx]
            typed = self.typed_words[idx] if idx < len(self.typed_words) else ""

            for j, ch in enumerate(typed):
                if j < len(target):
                    if ch == target[j]:
                        correct += 1
                    else:
                        incorrect += 1
                else:
                    extra += 1

            if idx < self.current_idx and len(typed) < len(target):
                missed += len(target) - len(typed)

        return CharStats(correct=correct, incorrect=incorrect, extra=extra, missed=missed)

    def get_live_wpm(self) -> float:
        """Calculate live Net WPM at the current moment."""
        elapsed = self.timer.elapsed()
        if elapsed < 0.5:
            return 0.0
        return calculate_wpm(self.get_correct_chars(strict=False), elapsed)

    def get_live_raw_wpm(self) -> float:
        """Calculate live Raw WPM at the current moment."""
        elapsed = self.timer.elapsed()
        if elapsed < 0.5:
            return 0.0
        return calculate_wpm(self.get_total_typed_chars(), elapsed)

    def get_live_accuracy(self) -> float:
        """Calculate live accuracy percentage."""
        return calculate_accuracy(self.correct_keystrokes, self.total_keystrokes)
