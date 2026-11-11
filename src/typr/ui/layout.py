"""Terminal layout and multi-line wrapping calculations for Typr."""

from __future__ import annotations

import unicodedata
from typing import List, Sequence, Tuple


def char_width(char: str) -> int:
    """Return terminal column width of a character (handling CJK/wide characters)."""
    if not char:
        return 0
    w = unicodedata.east_asian_width(char)
    return 2 if w in ("W", "F") else 1


def string_width(text: str) -> int:
    """Calculate terminal column display width of a string."""
    return sum(char_width(c) for c in text)


def effective_word_length(target_word: str, typed_word: str) -> int:
    """Calculate visual column length of a word, accounting for extra typed letters and wide chars."""
    return max(string_width(target_word), string_width(typed_word))


def compute_line_layout(
    target_words: Sequence[str],
    typed_words: Sequence[str],
    max_line_width: int,
    start_idx: int = 0,
    lookahead: int = 120,
    word_spacing: int = 1,
) -> List[List[int]]:
    """Partition words into wrapped display lines that fit within max_line_width.

    Returns:
        List of lines, where each line is a list of word indices.
    """
    end_idx = min(len(target_words), start_idx + lookahead)
    lines: List[List[int]] = [[]]
    current_x = 0

    for idx in range(end_idx):
        target = target_words[idx]
        typed = typed_words[idx] if idx < len(typed_words) else ""
        eff_len = effective_word_length(target, typed)

        # Space needed: eff_len + (word_spacing for inter-word space if not at start of line)
        needed = eff_len if current_x == 0 else current_x + word_spacing + eff_len
        if needed > max_line_width and current_x > 0:
            lines.append([])
            current_x = 0

        current_x = eff_len if current_x == 0 else current_x + word_spacing + eff_len
        lines[-1].append(idx)

    return lines


def calculate_active_window(
    lines: List[List[int]],
    active_word_idx: int,
    max_visible_lines: int = 3,
) -> Tuple[int, int]:
    """Determine which lines to render so the active word remains centered.

    Returns:
        (first_line_index, number_of_lines_to_display)
    """
    active_line_idx = 0
    for i, line in enumerate(lines):
        if active_word_idx in line:
            active_line_idx = i
            break

    # Center the active line: show 1 preceding line if available
    first_line = max(0, active_line_idx - 1)
    visible_count = min(len(lines) - first_line, max_visible_lines)
    return first_line, visible_count

