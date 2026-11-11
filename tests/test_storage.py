"""Unit tests for Typr configuration and history storage."""

import tempfile
import unittest
from pathlib import Path

from typr.core.metrics import CharStats
from typr.core.session import SessionConfig, TypingResult
from typr.storage.config import AppConfig, load_config, reset_config, save_config
from typr.storage.history import HistoryManager


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.cfg_file = Path(self.tmp_dir.name) / "config.json"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_default_config_validation(self):
        cfg = AppConfig()
        cfg.validate()
        self.assertEqual(cfg.theme, "mint")
        self.assertEqual(cfg.mode, "words")
        self.assertEqual(cfg.words, 25)
        self.assertFalse(cfg.focus_mode)
        self.assertEqual(cfg.text_size, "large")
        self.assertTrue(cfg.fade_completed)
        self.assertTrue(cfg.smooth_caret)

    def test_text_size_validation(self):
        cfg = AppConfig(text_size="invalid_size")
        cfg.validate()
        self.assertEqual(cfg.text_size, "large")

        cfg2 = AppConfig(text_size="normal")
        cfg2.validate()
        self.assertEqual(cfg2.text_size, "normal")

    def test_save_and_load_config(self):
        cfg = AppConfig(theme="amber", words=50, punctuation=True)
        save_config(cfg, self.cfg_file)
        self.assertTrue(self.cfg_file.exists())

        loaded = load_config(self.cfg_file)
        self.assertEqual(loaded.theme, "amber")
        self.assertEqual(loaded.words, 50)
        self.assertTrue(loaded.punctuation)

    def test_invalid_values_are_sanitized(self):
        bad_json = '{"theme": "nonexistent", "time": -50, "words": 9999}'
        self.cfg_file.write_text(bad_json, encoding="utf-8")
        loaded = load_config(self.cfg_file)
        self.assertEqual(loaded.theme, "mint")  # reset to default
        self.assertEqual(loaded.time, 5)        # clamped
        self.assertEqual(loaded.words, 1000)    # clamped

    def test_reset_config(self):
        cfg = AppConfig(theme="cyan", time=120)
        save_config(cfg, self.cfg_file)
        reset = reset_config(self.cfg_file)
        self.assertEqual(reset.theme, "mint")
        self.assertEqual(reset.time, 30)


class TestHistory(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_file = Path(self.tmp_dir.name) / "history.db"
        self.mgr = HistoryManager(self.db_file)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_empty_stats(self):
        stats = self.mgr.get_summary_stats()
        self.assertEqual(stats["total_tests"], 0)
        self.assertEqual(stats["avg_wpm"], 0.0)

    def test_record_and_pb_tracking(self):
        cfg = SessionConfig(mode="words", amount=25)
        res1 = TypingResult(
            net_wpm=55.0,
            raw_wpm=58.0,
            accuracy=96.0,
            consistency=88.0,
            duration=30.0,
            chars=CharStats(correct=150, incorrect=5),
            config=cfg,
        )
        is_pb1 = self.mgr.record_session(res1)
        self.assertTrue(is_pb1)
        self.assertEqual(self.mgr.get_personal_best(cfg), 55.0)

        # Second session with lower score is not PB
        res2 = TypingResult(
            net_wpm=50.0,
            raw_wpm=52.0,
            accuracy=95.0,
            consistency=85.0,
            duration=30.0,
            chars=CharStats(correct=140, incorrect=6),
            config=cfg,
        )
        is_pb2 = self.mgr.record_session(res2)
        self.assertFalse(is_pb2)
        self.assertEqual(self.mgr.get_personal_best(cfg), 55.0)

        # Third session with higher score is new PB
        res3 = TypingResult(
            net_wpm=65.0,
            raw_wpm=68.0,
            accuracy=98.0,
            consistency=92.0,
            duration=28.0,
            chars=CharStats(correct=160, incorrect=2),
            config=cfg,
        )
        is_pb3 = self.mgr.record_session(res3)
        self.assertTrue(is_pb3)
        self.assertEqual(self.mgr.get_personal_best(cfg), 65.0)

        # Check summary
        summary = self.mgr.get_summary_stats()
        self.assertEqual(summary["total_tests"], 3)
        self.assertAlmostEqual(summary["max_wpm"], 65.0)
        self.assertAlmostEqual(summary["avg_wpm"], (55.0 + 50.0 + 65.0) / 3.0)

        # Check recent sessions
        recent = self.mgr.get_recent_sessions(limit=5)
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[0]["net_wpm"], 65.0)

    def test_clear_history(self):
        cfg = SessionConfig(mode="words", amount=25)
        res = TypingResult(net_wpm=60.0, duration=25.0, config=cfg)
        self.mgr.record_session(res)
        self.assertEqual(self.mgr.get_summary_stats()["total_tests"], 1)

        self.mgr.clear_history()
        self.assertEqual(self.mgr.get_summary_stats()["total_tests"], 0)


if __name__ == "__main__":
    unittest.main()

