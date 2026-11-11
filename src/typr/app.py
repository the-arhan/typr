"""Application coordinator and interactive curses event loop for Typr."""

from __future__ import annotations

import curses
import locale
import sys
from typing import Optional

from typr.core.engine import TypingEngine
from typr.core.session import SessionState
from typr.modes import get_mode_handler
from typr.storage.config import AppConfig, load_config, save_config
from typr.storage.history import HistoryManager
from typr.ui.screens import (
    CODE_LANG_OPTIONS,
    DIFFICULTY_OPTIONS,
    MODE_OPTIONS,
    THEME_OPTIONS,
    TIME_OPTIONS,
    WORD_OPTIONS,
    render_menu_screen,
    render_results_screen,
    render_test_screen,
)
from typr.ui.terminal import reset_cursor_shape, safe_curses_run, set_cursor_shape
from typr.ui.themes import setup_theme_colors


class TyprApp:
    """Manages application state and the curses presentation loop."""

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or load_config()
        self.history = HistoryManager()
        self.current_screen = "test"  # "test", "results", "menu"
        self.config_dirty = False
        self.visual_caret: Optional[Tuple[float, float]] = None

        # Check UTF-8 support
        try:
            locale.setlocale(locale.LC_ALL, "")
            self.unicode_support = "utf" in locale.getpreferredencoding().lower()
        except locale.Error:
            self.unicode_support = True

        self.engine: TypingEngine = self._new_engine()

    def _new_engine(self) -> TypingEngine:
        handler = get_mode_handler(self.config.mode)
        return handler.build_engine(self.config)

    def launch(self) -> None:
        """Launch the curses application within a safe restoration harness."""
        try:
            safe_curses_run(self._run)
        finally:
            if self.config_dirty:
                save_config(self.config)

    def _run(self, scr: curses.window) -> None:
        attrs = setup_theme_colors(self.config.theme)
        scr.keypad(True)
        scr.timeout(50)  # 50ms tick rate
        set_cursor_shape(self.config.cursor_style)

        while True:
            rows, cols = scr.getmaxyx()

            # 1. Update session state
            if self.current_screen == "test":
                self.engine.tick()
                # Check for dynamic word buffer extension in time mode
                if (
                    self.config.mode == "time"
                    and self.engine.current_idx + 40 >= len(self.engine.target_words)
                ):
                    from typr.core.text_source import TextSource
                    src = TextSource(
                        wordlist_name=self.config.language,
                        punctuation=self.config.punctuation,
                        numbers=self.config.numbers,
                    )
                    self.engine.extend_words(src.generate_words(50))

                if self.engine.state in (SessionState.COMPLETED, SessionState.ABORTED):
                    if self.engine.result and self.config.save_history:
                        self.history.record_session(self.engine.result)
                    self.current_screen = "results"
                    continue

                pb = self.history.get_personal_best(self.engine.config)
                cursor_pos = render_test_screen(
                    scr,
                    attrs,
                    self.engine,
                    self.config,
                    personal_best=pb,
                    unicode_support=self.unicode_support,
                )

                # Hardware cursor & smooth caret management
                if cursor_pos and self.config.cursor_style != "off":
                    if not self.config.smooth_caret or self.visual_caret is None:
                        self.visual_caret = (float(cursor_pos[0]), float(cursor_pos[1]))
                    else:
                        # Snap immediately if line changed
                        if int(round(self.visual_caret[0])) != cursor_pos[0]:
                            self.visual_caret = (float(cursor_pos[0]), float(cursor_pos[1]))
                        else:
                            # Horizontal interpolation toward target
                            target_x = float(cursor_pos[1])
                            diff = target_x - self.visual_caret[1]
                            if abs(diff) < 0.2:
                                self.visual_caret = (float(cursor_pos[0]), target_x)
                            else:
                                step = diff * 0.65
                                if abs(step) < 0.5:
                                    step = 0.5 if diff > 0 else -0.5
                                new_x = self.visual_caret[1] + step
                                if (diff > 0 and new_x > target_x) or (diff < 0 and new_x < target_x):
                                    new_x = target_x
                                self.visual_caret = (float(cursor_pos[0]), new_x)

                    draw_y = max(0, min(int(round(self.visual_caret[0])), rows - 1))
                    draw_x = max(0, min(int(round(self.visual_caret[1])), cols - 1))
                    try:
                        curses.curs_set(1)
                        scr.move(draw_y, draw_x)
                    except curses.error:
                        pass
                else:
                    self.visual_caret = None
                    try:
                        curses.curs_set(0)
                    except curses.error:
                        pass

            elif self.current_screen == "results":
                try:
                    curses.curs_set(0)
                except curses.error:
                    pass
                render_results_screen(
                    scr,
                    attrs,
                    self.engine,
                    self.config,
                    unicode_support=self.unicode_support,
                )

            elif self.current_screen == "menu":
                try:
                    curses.curs_set(0)
                except curses.error:
                    pass
                render_menu_screen(scr, attrs, self.config)

            # Fast animation tick while caret is transitioning
            if (
                self.current_screen == "test"
                and self.config.smooth_caret
                and cursor_pos
                and self.visual_caret
                and abs(self.visual_caret[1] - cursor_pos[1]) > 0.2
            ):
                scr.timeout(20)
            else:
                scr.timeout(50)

            # 2. Acquire non-blocking key input
            try:
                key = scr.get_wch()
            except curses.error:
                continue

            if key == curses.KEY_RESIZE:
                continue

            # 3. Universal exit shortcuts (Ctrl+C / Ctrl+D)
            if key in ("\x03", "\x04"):
                return

            # 4. Screen-specific key routing
            if self.current_screen == "test":
                if key == "\x06":  # Ctrl+F -> Toggle Focus Mode seamlessly
                    self.config.focus_mode = not self.config.focus_mode
                    self.config_dirty = True
                    continue
                elif key == "\x1b":  # Escape -> Menu
                    self.current_screen = "menu"
                elif (
                    (self.config.quick_restart == "tab" and key == "\t")
                    or (self.config.quick_restart == "enter" and key in ("\n", "\r", curses.KEY_ENTER))
                ):
                    self.engine = self._new_engine()
                elif key in ("\x7f", "\b", curses.KEY_BACKSPACE):
                    self.engine.press_backspace()
                elif key == "\x17":  # Ctrl+W -> Delete Word
                    self.engine.delete_word()
                elif isinstance(key, str) and len(key) == 1 and (key.isprintable() or key == " "):
                    self.engine.press_key(key)

            elif self.current_screen == "results":
                if key in ("\n", "\r", "\t", curses.KEY_ENTER):
                    self.engine = self._new_engine()
                    self.current_screen = "test"
                elif key == "\x1b":
                    self.current_screen = "menu"
                elif key in ("q", "Q"):
                    return

            elif self.current_screen == "menu":
                if key in ("\n", "\r", curses.KEY_ENTER):
                    self.engine = self._new_engine()
                    self.current_screen = "test"
                elif key in ("q", "Q"):
                    return
                elif key == "\x1b":
                    self.current_screen = "test"
                elif isinstance(key, str):
                    if self._handle_menu_key(key):
                        attrs = setup_theme_colors(self.config.theme)
                        self.config_dirty = True

    def _handle_menu_key(self, key: str) -> bool:
        """Update settings based on menu hotkey. Returns True if modified."""
        if key in "1234":
            self.config.mode = "time"
            self.config.time = TIME_OPTIONS[int(key) - 1]
            return True
        elif key in "5678":
            self.config.mode = "words"
            self.config.words = WORD_OPTIONS[int(key) - 5]
            return True
        elif key == "m":
            cur_idx = MODE_OPTIONS.index(self.config.mode) if self.config.mode in MODE_OPTIONS else 0
            self.config.mode = MODE_OPTIONS[(cur_idx + 1) % len(MODE_OPTIONS)]
            return True
        elif key == "p":
            self.config.punctuation = not self.config.punctuation
            return True
        elif key == "n":
            self.config.numbers = not self.config.numbers
            return True
        elif key == "d":
            cur_idx = (
                DIFFICULTY_OPTIONS.index(self.config.difficulty)
                if self.config.difficulty in DIFFICULTY_OPTIONS
                else 0
            )
            self.config.difficulty = DIFFICULTY_OPTIONS[(cur_idx + 1) % len(DIFFICULTY_OPTIONS)]
            return True
        elif key == "t":
            cur_idx = (
                THEME_OPTIONS.index(self.config.theme)
                if self.config.theme in THEME_OPTIONS
                else 0
            )
            self.config.theme = THEME_OPTIONS[(cur_idx + 1) % len(THEME_OPTIONS)]
            return True
        elif key == "l" and self.config.mode == "code":
            cur_idx = (
                CODE_LANG_OPTIONS.index(self.config.code_language)
                if self.config.code_language in CODE_LANG_OPTIONS
                else 0
            )
            self.config.code_language = CODE_LANG_OPTIONS[(cur_idx + 1) % len(CODE_LANG_OPTIONS)]
            return True
        elif key == "f":
            self.config.focus_mode = not self.config.focus_mode
            return True
        elif key == "s":
            self.config.text_size = "normal" if self.config.text_size == "large" else "large"
            return True
        elif key == "c":
            self.config.smooth_caret = not self.config.smooth_caret
            return True
        elif key == "w":
            self.config.fade_completed = not self.config.fade_completed
            return True
        return False
