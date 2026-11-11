"""Terminal curses lifecycle and hardware cursor management."""

from __future__ import annotations

import curses
import os
import sys
from typing import Callable, Optional


def set_cursor_shape(style: str) -> None:
    """Configure terminal hardware cursor shape via DEC private escape sequences.

    Codes:
      1: Blinking block
      2: Steady block
      3: Blinking underline
      4: Steady underline
      5: Blinking bar / line
      6: Steady bar / line
    """
    code_map = {
        "line": "5",
        "block": "2",
        "underline": "4",
        "off": "0",
    }
    code = code_map.get(style, "5")
    try:
        sys.stdout.write(f"\x1b[{code} q")
        sys.stdout.flush()
    except (OSError, ValueError):
        pass


def reset_cursor_shape() -> None:
    """Restore default hardware cursor shape."""
    try:
        sys.stdout.write("\x1b[0 q")
        sys.stdout.flush()
    except (OSError, ValueError):
        pass


def safe_curses_run(callback: Callable[[curses.window], None]) -> None:
    """Execute callback within curses.wrapper, ensuring absolute cleanup on exit."""
    # Ensure snappy Escape key recognition
    os.environ.setdefault("ESCDELAY", "25")
    try:
        curses.wrapper(callback)
    finally:
        reset_cursor_shape()
        # Ensure echo and cursor visibility are restored even if curses was interrupted
        try:
            curses.echo()
            curses.nocbreak()
            curses.endwin()
        except curses.error:
            pass

