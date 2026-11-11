"""Unit tests for Typr core engine, metrics, and timer."""

import unittest
from typr.core.timer import SessionTimer
from typr.core.metrics import (
    calculate_wpm,
    calculate_accuracy,
    calculate_consistency,
    calculate_text_accuracy,
    CharStats,
)
from typr.core.session import SessionConfig, SessionState
from typr.core.engine import TypingEngine
from typr.core.text_source import TextSource, load_quotes, load_code_snippets


class TestTimer(unittest.TestCase):
    def test_timer_lifecycle(self):
        timer = SessionTimer()
        self.assertEqual(timer.elapsed(), 0.0)
        self.assertFalse(timer.is_running)

        timer.start()
        self.assertTrue(timer.is_running)
        self.assertFalse(timer.is_paused)
        self.assertFalse(timer.is_stopped)

        e1 = timer.elapsed()
        self.assertGreaterEqual(e1, 0.0)

        # Pause and resume
        timer.pause()
        self.assertTrue(timer.is_paused)
        self.assertFalse(timer.is_running)
        timer.resume()
        self.assertTrue(timer.is_running)

        # Stop
        dur = timer.stop()
        self.assertTrue(timer.is_stopped)
        self.assertFalse(timer.is_running)
        self.assertGreaterEqual(dur, 0.0)


class TestMetrics(unittest.TestCase):
    def test_wpm_calculation(self):
        self.assertAlmostEqual(calculate_wpm(50, 60.0), 10.0)
        self.assertEqual(calculate_wpm(50, 0.0), 0.0)
        self.assertEqual(calculate_wpm(0, 30.0), 0.0)

    def test_accuracy_calculation(self):
        self.assertAlmostEqual(calculate_accuracy(100, 100), 100.0)
        self.assertAlmostEqual(calculate_accuracy(95, 100), 95.0)
        self.assertAlmostEqual(calculate_accuracy(0, 0), 100.0)

    def test_text_accuracy_calculation(self):
        stats = CharStats(correct=90, incorrect=5, extra=3, missed=2)
        self.assertAlmostEqual(calculate_text_accuracy(stats), 90.0)
        empty_stats = CharStats()
        self.assertEqual(calculate_text_accuracy(empty_stats), 100.0)

    def test_consistency_calculation(self):
        self.assertAlmostEqual(calculate_consistency([60.0, 60.0, 60.0, 60.0]), 100.0)
        self.assertAlmostEqual(calculate_consistency([]), 100.0)
        self.assertAlmostEqual(calculate_consistency([50.0]), 100.0)
        # Moderate variation
        c = calculate_consistency([40.0, 60.0, 50.0, 55.0])
        self.assertGreater(c, 50.0)
        self.assertLessEqual(c, 100.0)


class TestTypingEngine(unittest.TestCase):
    def test_basic_typing_and_completion(self):
        words = ["hello", "world"]
        cfg = SessionConfig(mode="words", amount=2)
        engine = TypingEngine(cfg, words)

        self.assertEqual(engine.state, SessionState.READY)
        self.assertEqual(engine.current_idx, 0)

        for ch in "hello":
            self.assertTrue(engine.press_key(ch))

        self.assertEqual(engine.state, SessionState.RUNNING)
        self.assertEqual(engine.typed_words[0], "hello")

        self.assertTrue(engine.press_key(" "))
        self.assertEqual(engine.current_idx, 1)

        for ch in "world":
            self.assertTrue(engine.press_key(ch))

        self.assertEqual(engine.state, SessionState.COMPLETED)
        self.assertIsNotNone(engine.result)
        self.assertEqual(engine.result.accuracy, 100.0)
        self.assertGreater(engine.result.net_wpm, 0.0)
        self.assertIsNone(engine.result.failed_reason)

    def test_backspace_and_word_deletion(self):
        words = ["apple", "banana"]
        cfg = SessionConfig(mode="words", amount=2)
        engine = TypingEngine(cfg, words)

        for ch in "appx":
            engine.press_key(ch)
        self.assertEqual(engine.typed_words[0], "appx")

        engine.press_backspace()
        self.assertEqual(engine.typed_words[0], "app")

        engine.delete_word()
        self.assertEqual(engine.typed_words[0], "")

    def test_freedom_mode_backspacing(self):
        # Without freedom mode: cannot backspace into previous word if correct
        words = ["one", "two"]
        cfg_strict = SessionConfig(mode="words", amount=2, freedom_mode=False)
        engine_strict = TypingEngine(cfg_strict, words)
        for ch in "one":
            engine_strict.press_key(ch)
        engine_strict.press_space()
        self.assertEqual(engine_strict.current_idx, 1)
        self.assertFalse(engine_strict.can_backspace_to_previous_word())

        # With freedom mode: can backspace into previous word
        cfg_free = SessionConfig(mode="words", amount=2, freedom_mode=True)
        engine_free = TypingEngine(cfg_free, words)
        for ch in "one":
            engine_free.press_key(ch)
        engine_free.press_space()
        self.assertEqual(engine_free.current_idx, 1)
        self.assertTrue(engine_free.can_backspace_to_previous_word())
        engine_free.press_backspace()
        self.assertEqual(engine_free.current_idx, 0)

    def test_strict_space(self):
        words = ["correct", "word"]
        cfg = SessionConfig(mode="words", amount=2, strict_space=True)
        engine = TypingEngine(cfg, words)
        for ch in "correcx":
            engine.press_key(ch)
        # Attempt space on erroneous word
        res = engine.press_space()
        self.assertFalse(res)
        self.assertEqual(engine.current_idx, 0)

    def test_stop_on_error_letter(self):
        words = ["abc"]
        cfg = SessionConfig(mode="words", amount=1, stop_on_error="letter")
        engine = TypingEngine(cfg, words)
        # Correct 'a'
        self.assertTrue(engine.press_key("a"))
        # Incorrect 'z' should be blocked
        self.assertFalse(engine.press_key("z"))
        self.assertEqual(engine.typed_words[0], "a")

    def test_char_stats_calculation(self):
        words = ["test", "case"]
        cfg = SessionConfig(mode="words", amount=2)
        engine = TypingEngine(cfg, words)

        # Type 'txst' (1 correct, 1 incorrect, 2 correct)
        for ch in "txst":
            engine.press_key(ch)
        engine.press_space()

        # Type 'cas' (missed last 'e')
        for ch in "cas":
            engine.press_key(ch)

        stats = engine.get_char_stats()
        self.assertEqual(stats.correct, 6)    # 't', 's', 't' in first word + 'c', 'a', 's' in second
        self.assertEqual(stats.incorrect, 1)  # 'x'
        self.assertEqual(stats.extra, 0)

    def test_master_difficulty_failure(self):
        words = ["correct"]
        cfg = SessionConfig(mode="words", amount=1, difficulty="master")
        engine = TypingEngine(cfg, words)

        engine.press_key("c")
        self.assertEqual(engine.state, SessionState.RUNNING)

        engine.press_key("x")
        self.assertEqual(engine.state, SessionState.ABORTED)
        self.assertIsNotNone(engine.result)
        self.assertIn("master", engine.result.failed_reason)

    def test_expert_difficulty_failure(self):
        words = ["first", "second"]
        cfg = SessionConfig(mode="words", amount=2, difficulty="expert")
        engine = TypingEngine(cfg, words)

        for ch in "firsx":
            engine.press_key(ch)
        engine.press_space()

        self.assertEqual(engine.state, SessionState.ABORTED)
        self.assertIsNotNone(engine.result)
        self.assertIn("expert", engine.result.failed_reason)


class TestTextSource(unittest.TestCase):
    def test_word_generation(self):
        source = TextSource(seed=42)
        words = source.generate_words(10)
        self.assertEqual(len(words), 10)
        for w in words:
            self.assertGreater(len(w), 0)

    def test_quotes_loading(self):
        quotes = load_quotes()
        self.assertIsInstance(quotes, list)
        self.assertGreater(len(quotes), 0)
        self.assertIn("text", quotes[0])
        self.assertIn("source", quotes[0])

    def test_code_snippets_loading(self):
        for lang in ("python", "rust", "cpp", "javascript", "typescript", "go", "bash", "sql"):
            snippets = load_code_snippets(lang)
            self.assertIsInstance(snippets, list)
            self.assertGreater(len(snippets), 0)


if __name__ == "__main__":
    unittest.main()
