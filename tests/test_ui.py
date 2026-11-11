"""Unit tests for Typr UI layout and color mapping logic."""

import unittest
from typr.ui.layout import (
    effective_word_length,
    compute_line_layout,
    calculate_active_window,
)
from typr.ui.themes import hex_to_rgb, nearest_256_color, THEME_PALETTES


class TestUILayout(unittest.TestCase):
    def test_effective_word_length(self):
        self.assertEqual(effective_word_length("apple", "app"), 5)
        self.assertEqual(effective_word_length("apple", "applesauce"), 10)
        self.assertEqual(effective_word_length("test", "test"), 4)

    def test_compute_line_layout(self):
        words = ["one", "two", "three", "four", "five", "six", "seven", "eight"]
        typed = [""] * len(words)
        # With max width 15, words should wrap cleanly
        lines = compute_line_layout(words, typed, max_line_width=15)
        self.assertGreater(len(lines), 1)
        # All word indices should be present in order
        all_indices = [idx for line in lines for idx in line]
        self.assertEqual(all_indices, list(range(len(words))))

    def test_compute_line_layout_with_word_spacing(self):
        words = ["one", "two", "three", "four"]
        typed = [""] * len(words)
        # With word_spacing=2, more line breaks should occur for a constrained width
        lines_1 = compute_line_layout(words, typed, max_line_width=12, word_spacing=1)
        lines_2 = compute_line_layout(words, typed, max_line_width=12, word_spacing=2)
        self.assertGreaterEqual(len(lines_2), len(lines_1))

    def test_active_window_centering(self):
        lines = [[0, 1], [2, 3], [4, 5], [6, 7]]
        # Active word 0 (line 0) -> first line 0
        first_line, count = calculate_active_window(lines, active_word_idx=0, max_visible_lines=3)
        self.assertEqual(first_line, 0)
        self.assertEqual(count, 3)

        # Active word 4 (line 2) -> centers: first line 1
        first_line, count = calculate_active_window(lines, active_word_idx=4, max_visible_lines=3)
        self.assertEqual(first_line, 1)
        self.assertEqual(count, 3)


class TestThemes(unittest.TestCase):
    def test_hex_to_rgb(self):
        self.assertEqual(hex_to_rgb("#ffffff"), (255, 255, 255))
        self.assertEqual(hex_to_rgb("#000000"), (0, 0, 0))
        self.assertEqual(hex_to_rgb("#f00"), (255, 0, 0))

    def test_nearest_256_color(self):
        # Pure white -> 231 or 15 or 255
        idx_white = nearest_256_color("#ffffff")
        self.assertIn(idx_white, (15, 231, 255))
        # Pure black -> 16 or 232
        idx_black = nearest_256_color("#000000")
        self.assertIn(idx_black, (0, 16, 232))

    def test_palette_definitions(self):
        for name in ("mint", "amber", "cyan", "mono"):
            self.assertIn(name, THEME_PALETTES)
            palette = THEME_PALETTES[name]
            self.assertTrue(palette.accent.startswith("#"))
            self.assertTrue(palette.bg.startswith("#"))


if __name__ == "__main__":
    unittest.main()

