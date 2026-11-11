"""Monotonic session timer for Typr.

Provides drift-free timing using time.monotonic() with pause/resume support
and explicit bounds checking to prevent division by zero.
"""

from __future__ import annotations

import time
from typing import Optional


class SessionTimer:
    """A monotonic session timer with pause and elapsed calculation."""

    def __init__(self) -> None:
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None
        self._paused_at: Optional[float] = None
        self._total_paused: float = 0.0

    def start(self) -> None:
        """Start or restart the timer."""
        now = time.monotonic()
        self._start_time = now
        self._end_time = None
        self._paused_at = None
        self._total_paused = 0.0

    def pause(self) -> None:
        """Pause the running timer."""
        if self._start_time is not None and self._paused_at is None and self._end_time is None:
            self._paused_at = time.monotonic()

    def resume(self) -> None:
        """Resume a paused timer."""
        if self._paused_at is not None:
            self._total_paused += time.monotonic() - self._paused_at
            self._paused_at = None

    def stop(self) -> float:
        """Stop the timer and return the total elapsed duration in seconds."""
        if self._start_time is None:
            return 0.0
        if self._end_time is None:
            if self._paused_at is not None:
                self._end_time = self._paused_at
            else:
                self._end_time = time.monotonic()
        return self.elapsed()

    def elapsed(self) -> float:
        """Return elapsed duration in seconds, excluding pauses.

        Never returns negative values.
        """
        if self._start_time is None:
            return 0.0
        if self._end_time is not None:
            raw = self._end_time - self._start_time
        elif self._paused_at is not None:
            raw = self._paused_at - self._start_time
        else:
            raw = time.monotonic() - self._start_time

        effective = raw - self._total_paused
        return max(0.0, effective)

    @property
    def is_running(self) -> bool:
        """Return True if timer is currently running and not paused or stopped."""
        return self._start_time is not None and self._paused_at is None and self._end_time is None

    @property
    def is_paused(self) -> bool:
        """Return True if timer is paused."""
        return self._paused_at is not None and self._end_time is None

    @property
    def is_stopped(self) -> bool:
        """Return True if timer has been stopped."""
        return self._end_time is not None

