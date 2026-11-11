"""Unit tests for Typr application controller and menu hotkeys."""

import unittest
from typr.app import TyprApp
from typr.storage.config import AppConfig


class TestApp(unittest.TestCase):
    def setUp(self):
        self.cfg = AppConfig(theme="mint", mode="words", words=25, time=30)
        self.app = TyprApp(self.cfg)

    def test_menu_hotkeys_time(self):
        # 1 -> 15s, 2 -> 30s, 3 -> 60s, 4 -> 120s
        self.assertTrue(self.app._handle_menu_key("1"))
        self.assertEqual(self.app.config.mode, "time")
        self.assertEqual(self.app.config.time, 15)

        self.assertTrue(self.app._handle_menu_key("4"))
        self.assertEqual(self.app.config.time, 120)

    def test_menu_hotkeys_words(self):
        # 5 -> 10, 6 -> 25, 7 -> 50, 8 -> 100
        self.assertTrue(self.app._handle_menu_key("5"))
        self.assertEqual(self.app.config.mode, "words")
        self.assertEqual(self.app.config.words, 10)

        self.assertTrue(self.app._handle_menu_key("8"))
        self.assertEqual(self.app.config.words, 100)

    def test_menu_hotkeys_mode_toggle(self):
        # Initial mode words -> time -> quotes -> code -> words
        self.app.config.mode = "words"
        self.assertTrue(self.app._handle_menu_key("m"))
        self.assertEqual(self.app.config.mode, "time")
        self.assertTrue(self.app._handle_menu_key("m"))
        self.assertEqual(self.app.config.mode, "quotes")
        self.assertTrue(self.app._handle_menu_key("m"))
        self.assertEqual(self.app.config.mode, "code")
        self.assertTrue(self.app._handle_menu_key("m"))
        self.assertEqual(self.app.config.mode, "words")

    def test_menu_hotkeys_toggles(self):
        # p -> punctuation
        prev_p = self.app.config.punctuation
        self.assertTrue(self.app._handle_menu_key("p"))
        self.assertEqual(self.app.config.punctuation, not prev_p)

        # n -> numbers
        prev_n = self.app.config.numbers
        self.assertTrue(self.app._handle_menu_key("n"))
        self.assertEqual(self.app.config.numbers, not prev_n)

        # d -> difficulty
        self.assertTrue(self.app._handle_menu_key("d"))
        self.assertIn(self.app.config.difficulty, ("normal", "expert", "master"))

        # t -> theme
        self.assertTrue(self.app._handle_menu_key("t"))
        self.assertIn(self.app.config.theme, ("mint", "amber", "cyan", "mono"))

    def test_menu_hotkeys_display_options(self):
        # f -> focus_mode toggle
        prev_f = self.app.config.focus_mode
        self.assertTrue(self.app._handle_menu_key("f"))
        self.assertEqual(self.app.config.focus_mode, not prev_f)

        # s -> text_size toggle
        self.app.config.text_size = "large"
        self.assertTrue(self.app._handle_menu_key("s"))
        self.assertEqual(self.app.config.text_size, "normal")
        self.assertTrue(self.app._handle_menu_key("s"))
        self.assertEqual(self.app.config.text_size, "large")

        # c -> smooth_caret toggle
        prev_c = self.app.config.smooth_caret
        self.assertTrue(self.app._handle_menu_key("c"))
        self.assertEqual(self.app.config.smooth_caret, not prev_c)

        # w -> fade_completed toggle
        prev_w = self.app.config.fade_completed
        self.assertTrue(self.app._handle_menu_key("w"))
        self.assertEqual(self.app.config.fade_completed, not prev_w)

    def test_focus_mode_preserves_active_session(self):
        # Type a few characters in active test
        self.app.engine.press_key("a")
        self.app.engine.press_key("b")
        self.assertEqual(self.app.engine.typed_words[0], "ab")

        # Toggle focus mode
        self.app.config.focus_mode = not self.app.config.focus_mode

        # Engine state and typed characters must remain completely intact
        self.assertEqual(self.app.engine.typed_words[0], "ab")
        self.assertFalse(self.app.engine.timer.is_stopped)


if __name__ == "__main__":
    unittest.main()

