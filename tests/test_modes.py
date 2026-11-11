"""Unit tests for typing modes."""

import unittest
from typr.modes import get_mode_handler, WordsMode, TimeMode, QuotesMode, CodeMode
from typr.storage.config import AppConfig


class TestModes(unittest.TestCase):
    def test_words_mode(self):
        handler = get_mode_handler("words")
        self.assertIsInstance(handler, WordsMode)
        cfg = AppConfig(words=15, punctuation=True)
        engine = handler.build_engine(cfg)
        self.assertEqual(len(engine.target_words), 15)
        self.assertIn("words 15", handler.get_summary_label(cfg))

    def test_time_mode(self):
        handler = get_mode_handler("time")
        self.assertIsInstance(handler, TimeMode)
        cfg = AppConfig(time=45)
        engine = handler.build_engine(cfg)
        self.assertGreaterEqual(len(engine.target_words), 100)
        self.assertIn("time 45s", handler.get_summary_label(cfg))

    def test_quotes_mode(self):
        handler = get_mode_handler("quotes")
        self.assertIsInstance(handler, QuotesMode)
        cfg = AppConfig(mode="quotes")
        engine = handler.build_engine(cfg)
        self.assertGreater(len(engine.target_words), 0)

    def test_code_mode(self):
        handler = get_mode_handler("code")
        self.assertIsInstance(handler, CodeMode)
        for lang in ("python", "rust", "cpp", "javascript", "typescript", "go", "bash", "sql", "html", "css"):
            cfg = AppConfig(mode="code", code_language=lang)
            engine = handler.build_engine(cfg)
            self.assertGreater(len(engine.target_words), 0)
            self.assertIn(lang, handler.get_summary_label(cfg))


if __name__ == "__main__":
    unittest.main()

