"""Reusable terminal UI rendering components and widgets for Typr."""

from __future__ import annotations

import curses
import math
import unicodedata
from typing import Dict, List, Sequence


BAR_BLOCKS_UNICODE = " ▁▂▃▄▅▆▇█"
BAR_BLOCKS_ASCII = " .:-=+*##"


def char_width(char: str) -> int:
    """Return terminal column width of a character."""
    if not char:
        return 0
    w = unicodedata.east_asian_width(char)
    return 2 if w in ("W", "F") else 1


def safe_addstr(scr: curses.window, y: int, x: int, text: str, attr: int = 0) -> None:
    """Print text safely within screen boundaries, ignoring edge clipping errors."""
    rows, cols = scr.getmaxyx()
    if y < 0 or y >= rows or x < 0 or x >= cols:
        return
    clipped = text[: cols - x]
    if not clipped:
        return
    try:
        scr.addstr(y, x, clipped, attr)
    except curses.error:
        pass


def center_text(scr: curses.window, y: int, text: str, attr: int = 0) -> None:
    """Horizontally center text on line y."""
    _, cols = scr.getmaxyx()
    width = sum(char_width(c) for c in text)
    x = max(0, (cols - width) // 2)
    safe_addstr(scr, y, x, text, attr)


def draw_word(
    scr: curses.window,
    attrs: Dict[str, int],
    y: int,
    x: int,
    target_word: str,
    typed_word: str,
    is_past: bool = False,
    is_active: bool = False,
    fade_completed: bool = True,
) -> int:
    """Render an individual word with character-level accuracy highlighting and fading.

    Returns:
        The visual column width rendered.
    """
    total_len = max(len(target_word), len(typed_word))
    is_wrong_past = is_past and typed_word != target_word
    cur_x = x

    for i in range(total_len):
        if i < len(target_word):
            char = target_word[i]
            if i < len(typed_word):
                if typed_word[i] == char:
                    if is_past and fade_completed:
                        style = attrs.get("completed", attrs["muted"])
                    else:
                        style = attrs["correct"]
                else:
                    if is_past and fade_completed:
                        style = attrs.get("completed_error", attrs["error"])
                    else:
                        style = attrs["error"]
            else:
                if is_active:
                    style = attrs.get("active_untyped", attrs["text"])
                else:
                    style = attrs["untyped"]
        else:
            char = typed_word[i]
            if is_past and fade_completed:
                style = attrs.get("completed_error", attrs["error_extra"])
            else:
                style = attrs["error_extra"]

        if is_wrong_past:
            style |= curses.A_UNDERLINE

        safe_addstr(scr, y, cur_x, char, style)
        cur_x += char_width(char)

    return cur_x - x


def draw_wpm_graph(
    scr: curses.window,
    attrs: Dict[str, int],
    y: int,
    x: int,
    width: int,
    height: int,
    values: Sequence[float],
    unit: str = "wpm",
    unicode_bars: bool = True,
) -> None:
    """Render a terminal bar chart of typing speed over time."""
    if not values or height < 2 or width < 10:
        return

    vmax = math.ceil(max(max(values), 10.0) / 10.0) * 10
    vmin = 0
    span = max(float(vmax - vmin), 1.0)

    # Resample values to fit available width
    if len(values) > width:
        step = len(values) / width
        cols_val: List[float] = []
        for c in range(width):
            start = int(c * step)
            end = max(start + 1, int((c + 1) * step))
            chunk = values[start:end]
            cols_val.append(sum(chunk) / len(chunk))
    else:
        repeat = max(1, width // len(values))
        cols_val = [v for v in values for _ in range(repeat)][:width]

    height_levels = [int(round(max(0.0, v - vmin) / span * height * 8)) for v in cols_val]
    bars = BAR_BLOCKS_UNICODE if unicode_bars else BAR_BLOCKS_ASCII

    # Render vertical levels from top row to bottom row
    for row_idx in range(height):
        level = height - 1 - row_idx
        chars = []
        for h_val in height_levels:
            bracket = max(0, min(8, h_val - level * 8))
            chars.append(bars[bracket])
        row_str = "".join(chars)
        safe_addstr(scr, y + row_idx, x, row_str, attrs["accent"])

    # Graph axis labels
    safe_addstr(scr, y, x - 5, f"{int(vmax):>4}", attrs["muted"])
    safe_addstr(scr, y + height - 1, x - 5, f"{int(vmin):>4}", attrs["muted"])
    safe_addstr(scr, y + height, x, f"speed ({unit}) over time", attrs["muted"])

