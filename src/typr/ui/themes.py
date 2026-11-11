"""Independent color system and theme definitions for Typr.

Supports 256-color terminals, truecolor terminals, and high-contrast
monochrome profiles with non-color attribute styling (underline, bold, dim).
"""

from __future__ import annotations

import curses
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class ThemePalette:
    """Color palette definition using standard hex codes."""

    name: str
    bg: str
    surface: str
    text_primary: str
    text_muted: str
    accent: str
    error: str
    error_extra: str
    cursor: str
    warning: str


THEME_PALETTES: Dict[str, ThemePalette] = {
    # Graphite + Electric Mint (Default)
    "mint": ThemePalette(
        name="mint",
        bg="#18191c",
        surface="#222428",
        text_primary="#e2e4e9",
        text_muted="#525866",
        accent="#00f59b",
        error="#ff5c5c",
        error_extra="#d63333",
        cursor="#00f59b",
        warning="#e5c07b",
    ),
    # Obsidian + Warm Amber
    "amber": ThemePalette(
        name="amber",
        bg="#121214",
        surface="#1e1e24",
        text_primary="#f3ede2",
        text_muted="#5c564c",
        accent="#f5a623",
        error="#ff4d4d",
        error_extra="#c0392b",
        cursor="#ffb84d",
        warning="#e67e22",
    ),
    # Deep Navy + Restrained Cyan
    "cyan": ThemePalette(
        name="cyan",
        bg="#0d1117",
        surface="#161b22",
        text_primary="#c9d1d9",
        text_muted="#484f58",
        accent="#58a6ff",
        error="#ff7b72",
        error_extra="#da3633",
        cursor="#79c0ff",
        warning="#d29922",
    ),
    # High-contrast monochrome profile
    "mono": ThemePalette(
        name="mono",
        bg="#000000",
        surface="#111111",
        text_primary="#ffffff",
        text_muted="#888888",
        accent="#ffffff",
        error="#ffffff",
        error_extra="#888888",
        cursor="#ffffff",
        warning="#ffffff",
    ),
}


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Parse a 3 or 6 digit hex color code into (r, g, b) integers."""
    hex_code = hex_code.lstrip("#")
    if len(hex_code) == 3:
        hex_code = "".join(c * 2 for c in hex_code)
    try:
        return int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
    except (ValueError, IndexError):
        return (255, 255, 255)


def nearest_256_color(hex_code: str) -> int:
    """Map RGB hex code to nearest xterm-256 color index via Euclidean distance."""
    r, g, b = hex_to_rgb(hex_code)
    steps = (0, 95, 135, 175, 215, 255)

    # Find closest coordinate in 6x6x6 color cube
    r_idx = min(range(6), key=lambda i: abs(steps[i] - r))
    g_idx = min(range(6), key=lambda i: abs(steps[i] - g))
    b_idx = min(range(6), key=lambda i: abs(steps[i] - b))
    cube_idx = 16 + 36 * r_idx + 6 * g_idx + b_idx
    cube_dist = (r - steps[r_idx]) ** 2 + (g - steps[g_idx]) ** 2 + (b - steps[b_idx]) ** 2

    # Find closest coordinate in 24-step grayscale ramp
    gray_idx = min(23, max(0, round(((r + g + b) / 3 - 8) / 10)))
    gray_val = 8 + 10 * gray_idx
    gray_dist = (r - gray_val) ** 2 + (g - gray_val) ** 2 + (b - gray_val) ** 2

    return cube_idx if cube_dist <= gray_dist else 232 + gray_idx


def setup_theme_colors(theme_name: str) -> Dict[str, int]:
    """Initialize curses color pairs and return attribute dictionary."""
    palette = THEME_PALETTES.get(theme_name, THEME_PALETTES["mint"])
    curses.start_color()

    try:
        curses.use_default_colors()
        bg = -1
    except curses.error:
        bg = curses.COLOR_BLACK

    has_256 = getattr(curses, "COLORS", 8) >= 256
    is_mono = theme_name == "mono"

    if has_256 and not is_mono:
        c_accent = nearest_256_color(palette.accent)
        c_text = nearest_256_color(palette.text_primary)
        c_muted = nearest_256_color(palette.text_muted)
        c_err = nearest_256_color(palette.error)
        c_err_extra = nearest_256_color(palette.error_extra)
        c_warn = nearest_256_color(palette.warning)
    else:
        c_accent = curses.COLOR_WHITE if is_mono else curses.COLOR_GREEN
        c_text = curses.COLOR_WHITE
        c_muted = curses.COLOR_WHITE
        c_err = curses.COLOR_WHITE if is_mono else curses.COLOR_RED
        c_err_extra = curses.COLOR_WHITE if is_mono else curses.COLOR_RED
        c_warn = curses.COLOR_WHITE if is_mono else curses.COLOR_YELLOW

    # Register pairs 1-6
    curses.init_pair(1, c_accent, bg)
    curses.init_pair(2, c_text, bg)
    curses.init_pair(3, c_muted, bg)
    curses.init_pair(4, c_err, bg)
    curses.init_pair(5, c_err_extra, bg)
    curses.init_pair(6, c_warn, bg)

    attrs = {
        "accent": curses.color_pair(1) | curses.A_BOLD,
        "text": curses.color_pair(2),
        "muted": curses.color_pair(3),
        "untyped": curses.color_pair(3) | (curses.A_DIM if not is_mono else 0),
        "active_untyped": curses.color_pair(3),
        "correct": curses.color_pair(2) | curses.A_BOLD,
        "error": curses.color_pair(4) | curses.A_UNDERLINE,
        "error_extra": curses.color_pair(5) | curses.A_UNDERLINE,
        "warning": curses.color_pair(6),
        "completed": curses.color_pair(3) | curses.A_DIM,
        "completed_error": curses.color_pair(4) | curses.A_DIM | curses.A_UNDERLINE,
        "active": curses.color_pair(2) | curses.A_BOLD,
        "caret": curses.color_pair(1) | curses.A_BOLD,
    }

    if is_mono or not has_256:
        attrs["muted"] = curses.A_DIM
        attrs["untyped"] = curses.A_DIM
        attrs["active_untyped"] = curses.A_NORMAL
        attrs["completed"] = curses.A_DIM
        attrs["completed_error"] = curses.A_UNDERLINE | curses.A_DIM
        attrs["correct"] = curses.A_BOLD
        attrs["error"] = curses.A_UNDERLINE | curses.A_BOLD
        attrs["caret"] = curses.A_REVERSE

    return attrs

