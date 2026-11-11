"""Terminal UI, themes, widgets, and screen renderers for Typr."""

from typr.ui.layout import calculate_active_window, compute_line_layout, effective_word_length
from typr.ui.screens import (
    render_menu_screen,
    render_results_screen,
    render_test_screen,
)
from typr.ui.terminal import reset_cursor_shape, safe_curses_run, set_cursor_shape
from typr.ui.themes import THEME_PALETTES, setup_theme_colors
from typr.ui.widgets import center_text, draw_word, draw_wpm_graph, safe_addstr

__all__ = [
    "setup_theme_colors",
    "THEME_PALETTES",
    "safe_curses_run",
    "set_cursor_shape",
    "reset_cursor_shape",
    "compute_line_layout",
    "calculate_active_window",
    "effective_word_length",
    "safe_addstr",
    "center_text",
    "draw_word",
    "draw_wpm_graph",
    "render_test_screen",
    "render_results_screen",
    "render_menu_screen",
]

