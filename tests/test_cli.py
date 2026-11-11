"""Unit tests for Typr CLI argument parsing and utility actions."""

import io
import sys
import unittest
from unittest.mock import patch

from typr.cli import main, parse_args
from typr.storage.config import load_config


class TestCLI(unittest.TestCase):
    def test_argument_parsing_defaults(self):
        args = parse_args([])
        self.assertIsNone(args.time)
        self.assertIsNone(args.words)
        self.assertIsNone(args.mode)
        self.assertFalse(args.punctuation)
        self.assertFalse(args.numbers)

    def test_custom_flags(self):
        args = parse_args([
            "-t", "45", "-p", "-n",
            "--theme", "amber",
            "--difficulty", "master",
            "--focus",
            "--text-size", "large",
            "--no-smooth-caret",
            "--no-fade",
        ])
        self.assertEqual(args.time, 45)
        self.assertTrue(args.punctuation)
        self.assertTrue(args.numbers)
        self.assertEqual(args.theme, "amber")
        self.assertEqual(args.difficulty, "master")
        self.assertTrue(args.focus)
        self.assertEqual(args.text_size, "large")
        self.assertTrue(args.no_smooth_caret)
        self.assertTrue(args.no_fade)

    def test_mutually_exclusive_time_and_words(self):
        with self.assertRaises(SystemExit):
            with patch("sys.stderr", new_callable=io.StringIO):
                parse_args(["-t", "30", "-w", "50"])

    def test_config_path_exit(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["--config-path"])
            self.assertEqual(code, 0)
            self.assertIn("config.json", mock_out.getvalue())

    def test_stats_flag(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["--stats"])
            self.assertEqual(code, 0)
            self.assertIn("TYPR PERFORMANCE ANALYTICS", mock_out.getvalue())

    def test_history_flag(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["--history"])
            self.assertEqual(code, 0)

    def test_reset_config_flag(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["--reset-config"])
            self.assertEqual(code, 0)
            self.assertIn("Configuration reset", mock_out.getvalue())

    def test_clear_history_flag(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["--clear-history"])
            self.assertEqual(code, 0)
            self.assertIn("Local session history cleared", mock_out.getvalue())


if __name__ == "__main__":
    unittest.main()

