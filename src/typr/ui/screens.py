"""Interactive terminal screens for Typr: Test, Results, and Menu."""

from __future__ import annotations

import curses
import math
from typing import Dict, List, Optional, Tuple

from typr.core.engine import TypingEngine
from typr.core.session import SessionState, TypingResult
from typr.storage.config import AppConfig
from typr.ui.layout import (
    calculate_active_window,
    compute_line_layout,
    effective_word_length,
    string_width,
)
from typr.ui.widgets import center_text, draw_word, draw_wpm_graph, safe_addstr


TIME_OPTIONS = [15, 30, 60, 120]
WORD_OPTIONS = [10, 25, 50, 100]
THEME_OPTIONS = ["mint", "amber", "cyan", "mono"]
MODE_OPTIONS = ["words", "time", "quotes", "code"]
CODE_LANG_OPTIONS = ["python", "rust", "cpp", "javascript", "typescript", "go", "bash", "sql", "html", "css"]
DIFFICULTY_OPTIONS = ["normal", "expert", "master"]


def render_test_screen(
    scr: curses.window,
    attrs: Dict[str, int],
    engine: TypingEngine,
    config: AppConfig,
    personal_best: float = 0.0,
    unicode_support: bool = True,
) -> Optional[Tuple[int, int]]:
    """Render the active typing screen with Normal and Focus mode support.

    Returns:
        (cursor_y, cursor_x) coordinate to place the hardware/visual cursor, or None.
    """
    scr.erase()
    rows, cols = scr.getmaxyx()

    if rows < 10 or cols < 36:
        safe_addstr(scr, 0, 0, "Terminal window too small", attrs["error"])
        scr.refresh()
        return None

    # Line width clamped between 30 and max_line_width with comfortable margin
    usable_width = min(cols - 8, config.max_line_width)
    x0 = max(0, (cols - usable_width) // 2)

    # Adaptive row and inter-word spacing for spacious, comfortable typography
    row_spacing = 3 if rows >= 24 and config.text_size in ("large", "adaptive") else 2
    word_spacing = 2 if config.text_size in ("large", "adaptive") and engine.config.mode != "code" and cols >= 80 else 1

    # 1. Normal Mode Chrome (Hidden completely in Focus Mode)
    if not config.focus_mode:
        # Top Bar
        safe_addstr(scr, 1, x0, "typr", attrs["accent"])
        safe_addstr(scr, 1, x0 + 7, f"•  {engine.config.label}", attrs["muted"])
        hint_menu = "ctrl+f: focus   esc: menu"
        safe_addstr(scr, 1, max(x0 + 20, x0 + usable_width - len(hint_menu)), hint_menu, attrs["muted"])

        # Live Telemetry
        elapsed = engine.timer.elapsed()
        telemetry_parts: List[str] = []

        if config.timer_style != "off":
            if engine.config.mode == "time":
                remaining = max(0.0, engine.config.amount - elapsed)
                telemetry_parts.append(f"{math.ceil(remaining)}s")
            else:
                telemetry_parts.append(f"{engine.current_idx}/{len(engine.target_words)}")

        if config.live_wpm and elapsed >= 1.0:
            telemetry_parts.append(f"{int(engine.get_live_wpm())} wpm")

        if config.live_acc and engine.total_keystrokes > 0:
            telemetry_parts.append(f"{int(engine.get_live_accuracy())}% acc")

        if config.live_burst and engine.current_burst:
            telemetry_parts.append(f"{int(engine.current_burst)} burst")

        if personal_best > 0.0:
            pb_str = f"pb: {int(personal_best)}"
            safe_addstr(scr, 3, max(x0, x0 + usable_width - len(pb_str)), pb_str, attrs["muted"])

        if telemetry_parts:
            safe_addstr(scr, 3, x0, "   ".join(telemetry_parts), attrs["accent"])

    # 2. Target Text Canvas (Centered with generous breathing room)
    lines = compute_line_layout(
        engine.target_words,
        engine.typed_words,
        usable_width,
        start_idx=max(0, engine.current_idx - 10),
        word_spacing=word_spacing,
    )
    first_line_idx, line_count = calculate_active_window(lines, engine.current_idx, max_visible_lines=3)

    if config.focus_mode:
        # In focus mode, center the passage vertically in the entire viewport
        canvas_top = max(2, (rows - (line_count * row_spacing)) // 2)
    else:
        canvas_top = max(5, rows // 2 - 2)

    cursor_pos: Optional[Tuple[int, int]] = None

    for r in range(line_count):
        line_idx = first_line_idx + r
        if line_idx >= len(lines):
            break
        y = canvas_top + (r * row_spacing)
        if y >= rows - 2:
            break

        cur_x = x0
        for word_idx in lines[line_idx]:
            target_word = engine.target_words[word_idx]
            typed_word = (
                engine.typed_words[word_idx]
                if word_idx < len(engine.typed_words)
                else ""
            )
            is_past = word_idx < engine.current_idx
            is_active = word_idx == engine.current_idx

            eff_len = draw_word(
                scr,
                attrs,
                y,
                cur_x,
                target_word,
                typed_word,
                is_past=is_past,
                is_active=is_active,
                fade_completed=config.fade_completed,
            )

            if is_active:
                typed_col = string_width(typed_word)
                cursor_pos = (y, cur_x + min(typed_col, eff_len))

            cur_x += eff_len + word_spacing

    # 3. Bottom Hints (Only in Normal Mode)
    if not config.focus_mode:
        hint_text = f"[{config.quick_restart}] restart   [ctrl+f] focus   [esc] menu   [ctrl+w] del-word"
        center_text(scr, rows - 2, hint_text, attrs["muted"])

    scr.refresh()
    return cursor_pos


def render_results_screen(
    scr: curses.window,
    attrs: Dict[str, int],
    engine: TypingEngine,
    config: AppConfig,
    unicode_support: bool = True,
) -> None:
    """Render the detailed results view with metrics grid and WPM timeline graph."""
    scr.erase()
    rows, cols = scr.getmaxyx()
    res = engine.result

    if not res:
        safe_addstr(scr, 2, 2, "No session results available.", attrs["error"])
        scr.refresh()
        return

    usable_width = min(cols - 8, config.max_line_width)
    x0 = max(0, (cols - usable_width) // 2)

    # Header / Title
    status_title = "SESSION RESULTS"
    status_attr = attrs["accent"]
    if res.failed_reason:
        status_title = f"FAILED: {res.failed_reason.upper()}"
        status_attr = attrs["error"]

    safe_addstr(scr, 1, x0, status_title, status_attr)

    # 2x4 Metric Grid items: (Label, Value)
    items = [
        ("WPM", f"{int(res.net_wpm)}"),
        ("ACCURACY", f"{res.accuracy:.1f}%"),
        ("RAW SPEED", f"{int(res.raw_wpm)} wpm"),
        ("CONSISTENCY", f"{res.consistency:.1f}%"),
        ("MODE", engine.config.label),
        ("CHARACTERS", f"{res.chars.correct}/{res.chars.incorrect}/{res.chars.extra}/{res.chars.missed}"),
        ("DURATION", f"{res.duration:.1f}s"),
        ("PERSONAL BEST", f"{int(res.personal_best)} wpm" + (" (NEW PB!)" if res.new_pb else "")),
    ]

    # Render metric boxes
    if cols >= 70:
        for idx, (label, val) in enumerate(items):
            col_idx = idx % 4
            row_idx = idx // 4
            box_x = x0 + (col_idx * (usable_width // 4))
            box_y = 3 + (row_idx * 3)

            safe_addstr(scr, box_y, box_x, label, attrs["muted"])
            val_style = attrs["accent"] if idx == 0 or (idx == 7 and res.new_pb) else attrs["text"]
            safe_addstr(scr, box_y + 1, box_x, val, val_style)

        graph_y = 10
    else:
        for idx, (label, val) in enumerate(items):
            safe_addstr(scr, 3 + idx, x0, f"{label:<14}", attrs["muted"])
            safe_addstr(scr, 3 + idx, x0 + 15, val, attrs["text"])
        graph_y = 3 + len(items) + 1

    # WPM Graph
    graph_h = min(8, rows - graph_y - 4)
    if graph_h >= 3 and res.timeline:
        draw_wpm_graph(
            scr,
            attrs,
            y=graph_y,
            x=x0 + 5,
            width=usable_width - 8,
            height=graph_h,
            values=res.timeline,
            unicode_bars=unicode_support,
        )

    # Bottom navigation hints
    center_text(scr, rows - 2, "enter/tab: next test   esc: menu   q: quit", attrs["muted"])
    scr.refresh()


def render_menu_screen(
    scr: curses.window,
    attrs: Dict[str, int],
    config: AppConfig,
) -> None:
    """Render the keyboard-driven configuration and settings screen."""
    scr.erase()
    rows, cols = scr.getmaxyx()
    y = max(2, rows // 2 - 7)

    center_text(scr, y, "TYPR SETTINGS", attrs["accent"])

    def format_row(label: str, options: Sequence[Tuple[str, str, bool]]) -> str:
        parts = [f"{label:<12}"]
        for key, name, is_active in options:
            bracket = f"[{key}] {name}"
            parts.append(f"{bracket:<12}" if not is_active else f"*{bracket}*   ")
        return "".join(parts)

    # Time Options (1-4)
    time_opts = [(str(i + 1), f"{t}s", config.mode == "time" and config.time == t) for i, t in enumerate(TIME_OPTIONS)]
    center_text(scr, y + 2, format_row("Time", time_opts), attrs["text"])

    # Words Options (5-8)
    word_opts = [(str(i + 5), f"{w}", config.mode == "words" and config.words == w) for i, w in enumerate(WORD_OPTIONS)]
    center_text(scr, y + 4, format_row("Words", word_opts), attrs["text"])

    # Mode Options (m)
    mode_opts = [
        ("m", f"mode: {config.mode}", True),
        ("p", f"punct: {'on' if config.punctuation else 'off'}", config.punctuation),
        ("n", f"nums: {'on' if config.numbers else 'off'}", config.numbers),
    ]
    center_text(scr, y + 6, format_row("Modes", mode_opts), attrs["text"])

    # Difficulty & Theme
    settings_opts = [
        ("d", f"diff: {config.difficulty}", config.difficulty != "normal"),
        ("t", f"theme: {config.theme}", True),
    ]
    if config.mode == "code":
        settings_opts.append(("l", f"lang: {config.code_language}", True))
    center_text(scr, y + 8, format_row("Options", settings_opts), attrs["text"])

    # Visual Experience & Focus Mode
    display_opts = [
        ("f", f"focus: {'on' if config.focus_mode else 'off'}", config.focus_mode),
        ("s", f"size: {config.text_size}", config.text_size == "large"),
        ("c", f"caret: {'smooth' if config.smooth_caret else 'direct'}", config.smooth_caret),
        ("w", f"fade: {'on' if config.fade_completed else 'off'}", config.fade_completed),
    ]
    center_text(scr, y + 10, format_row("Display", display_opts), attrs["text"])

    center_text(scr, y + 13, "enter: start test   esc: back   q: quit", attrs["muted"])
    scr.refresh()

