"""Standardized typing metrics calculations for Typr.

All calculations use published competition typing standards:
- 1 standard word = 5 characters (including spaces and punctuation).
- Net WPM = (correct characters / 5) / elapsed minutes.
- Raw WPM = (total typed characters / 5) / elapsed minutes.
- Accuracy = (correct keystrokes / total keystrokes) * 100.
- Consistency = normalized 0-100% score based on variance in burst typing speed.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class CharStats:
    """Detailed character accuracy breakdown."""

    correct: int = 0
    incorrect: int = 0
    extra: int = 0
    missed: int = 0

    @property
    def total_attempted(self) -> int:
        """Total characters attempted in the session."""
        return self.correct + self.incorrect + self.extra


def calculate_wpm(characters: int, seconds: float) -> float:
    """Calculate Words Per Minute based on standard 5-character word convention.

    Args:
        characters: Count of characters (correct characters for Net WPM,
                    total typed characters for Raw WPM).
        seconds: Elapsed duration in seconds.

    Returns:
        Words per minute (non-negative float).
    """
    if seconds <= 0.001 or characters <= 0:
        return 0.0
    minutes = seconds / 60.0
    return (characters / 5.0) / minutes


def calculate_accuracy(correct_keystrokes: int, total_keystrokes: int) -> float:
    """Calculate attempt-based typing accuracy percentage.

    Args:
        correct_keystrokes: Number of valid, matching key inputs.
        total_keystrokes: Total user key inputs registered.

    Returns:
        Accuracy percentage clamped between 0.0 and 100.0.
    """
    if total_keystrokes <= 0:
        return 100.0
    acc = (correct_keystrokes / total_keystrokes) * 100.0
    return max(0.0, min(100.0, acc))


def calculate_text_accuracy(stats: CharStats) -> float:
    """Calculate final text accuracy based on final character states."""
    total = stats.correct + stats.incorrect + stats.extra + stats.missed
    if total <= 0:
        return 100.0
    return max(0.0, min(100.0, (stats.correct / total) * 100.0))


def calculate_consistency(burst_speeds: Sequence[float]) -> float:
    """Calculate typing consistency score (0 - 100%) from speed samples.

    Uses the statistical Coefficient of Variation (CV = standard_deviation / mean).
    A lower CV indicates smoother, more consistent cadence.
    Score is mapped to a 0-100 scale: score = max(0.0, 100.0 * (1.0 - CV)).
    """
    if len(burst_speeds) < 2:
        return 100.0

    mean_val = sum(burst_speeds) / len(burst_speeds)
    if mean_val <= 0.0001:
        return 0.0

    variance = sum((x - mean_val) ** 2 for x in burst_speeds) / len(burst_speeds)
    std_dev = math.sqrt(variance)
    cv = std_dev / mean_val

    # Convert CV to a percentage consistency rating (100% = perfectly steady)
    score = 100.0 * (1.0 - cv)
    return max(0.0, min(100.0, score))

