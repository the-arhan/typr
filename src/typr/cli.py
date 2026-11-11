"""Command-line interface and argument router for Typr."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import Optional, Sequence

from typr import __version__
from typr.app import TyprApp
from typr.storage.config import load_config, reset_config, save_config
from typr.storage.history import HistoryManager
from typr.storage.paths import get_config_file, get_history_db_file


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Configure and parse command line flags."""
    parser = argparse.ArgumentParser(
        prog="typr",
        description="Typr — Terminal-native typing trainer built for people who live in the terminal.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"typr {__version__}")

    # Mode and test configuration
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-t",
        "--time",
        type=int,
        metavar="SECONDS",
        help="Run a timed typing session (e.g. 15, 30, 60)",
    )
    group.add_argument(
        "-w",
        "--words",
        type=int,
        metavar="COUNT",
        help="Run a word count typing session (e.g. 10, 25, 50)",
    )

    parser.add_argument(
        "-m",
        "--mode",
        choices=["words", "time", "quotes", "code"],
        help="Select typing mode (words, time, quotes, code)",
    )
    parser.add_argument(
        "-p",
        "--punctuation",
        action="store_true",
        help="Include punctuation in generated text",
    )
    parser.add_argument(
        "-n",
        "--numbers",
        action="store_true",
        help="Include numbers in generated text",
    )
    parser.add_argument(
        "-l",
        "--language",
        metavar="LANG",
        help="Language or programming language (e.g. python, rust, cpp, go, sql)",
    )
    parser.add_argument(
        "--theme",
        choices=["mint", "amber", "cyan", "mono"],
        help="Visual theme (mint, amber, cyan, mono)",
    )
    parser.add_argument(
        "--difficulty",
        choices=["normal", "expert", "master"],
        help="Difficulty constraint (normal, expert, master)",
    )
    parser.add_argument(
        "--focus",
        action="store_true",
        help="Start directly in distraction-free Focus mode",
    )
    parser.add_argument(
        "--text-size",
        choices=["normal", "large", "adaptive"],
        help="Typography size and layout breathing room",
    )
    parser.add_argument(
        "--no-smooth-caret",
        action="store_true",
        help="Disable smooth caret following animation",
    )
    parser.add_argument(
        "--no-fade",
        action="store_true",
        help="Disable fading of successfully completed words",
    )

    # Utilities and inspection flags
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Display aggregated performance statistics and exit",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Display recent typing session history and exit",
    )
    parser.add_argument(
        "--config-path",
        action="store_true",
        help="Print path to configuration file and exit",
    )
    parser.add_argument(
        "--reset-config",
        action="store_true",
        help="Reset configuration to factory defaults and exit",
    )
    parser.add_argument(
        "--clear-history",
        action="store_true",
        help="Clear local SQLite session history and exit",
    )

    return parser.parse_args(args)


def display_stats(history: HistoryManager) -> None:
    """Print clean terminal statistics summary without initializing curses."""
    stats = history.get_summary_stats()
    print("\n  \033[1;32mTYPR PERFORMANCE ANALYTICS\033[0m")
    print("  " + "─" * 40)
    print(f"  Total Sessions:     {stats['total_tests']}")
    mins = int(stats["total_time_seconds"] // 60)
    secs = int(stats["total_time_seconds"] % 60)
    print(f"  Total Time Typed:   {mins}m {secs}s")
    print(f"  Overall Average:    {stats['avg_wpm']:.1f} WPM")
    print(f"  Top Net Speed:      {stats['max_wpm']:.1f} WPM")
    print(f"  Average Accuracy:   {stats['avg_accuracy']:.1f}%")
    print("  " + "─" * 40 + "\n")


def display_history(history: HistoryManager) -> None:
    """Print recent sessions table without initializing curses."""
    sessions = history.get_recent_sessions(limit=10)
    if not sessions:
        print("\n  No sessions recorded yet. Run `typr` to start typing!\n")
        return

    print("\n  \033[1;32mRECENT TYPR SESSIONS\033[0m")
    print("  " + "─" * 68)
    print(f"  {'Date & Time':<18} {'Mode':<15} {'WPM':<8} {'Acc':<8} {'Time':<8} {'PB'}")
    print("  " + "─" * 68)

    for s in sessions:
        dt = datetime.fromtimestamp(s["timestamp"]).strftime("%Y-%m-%d %H:%M")
        mode_str = f"{s['mode']} {s['amount']}"
        pb_badge = "★ NEW" if s["is_pb"] else ""
        print(
            f"  {dt:<18} {mode_str:<15} {s['net_wpm']:<8.1f} {s['accuracy']:<8.1f}% {s['duration']:<7.1f}s {pb_badge}"
        )
    print("  " + "─" * 68 + "\n")


def main(args: Optional[Sequence[str]] = None) -> int:
    """Main CLI entry point."""
    parsed = parse_args(args)
    history = HistoryManager()

    # Utility operations
    if parsed.config_path:
        print(get_config_file())
        return 0

    if parsed.reset_config:
        reset_config()
        print(f"Configuration reset to defaults at {get_config_file()}")
        return 0

    if parsed.clear_history:
        history.clear_history()
        print(f"Local session history cleared ({get_history_db_file()})")
        return 0

    if parsed.stats:
        display_stats(history)
        return 0

    if parsed.history:
        display_history(history)
        return 0

    # Load and customize configuration
    cfg = load_config()

    if parsed.time:
        cfg.mode = "time"
        cfg.time = parsed.time
    elif parsed.words:
        cfg.mode = "words"
        cfg.words = parsed.words

    if parsed.mode:
        cfg.mode = parsed.mode
    if parsed.punctuation:
        cfg.punctuation = True
    if parsed.numbers:
        cfg.numbers = True
    if parsed.theme:
        cfg.theme = parsed.theme
    if parsed.difficulty:
        cfg.difficulty = parsed.difficulty
    if parsed.focus:
        cfg.focus_mode = True
    if parsed.text_size:
        cfg.text_size = parsed.text_size
    if parsed.no_smooth_caret:
        cfg.smooth_caret = False
    if parsed.no_fade:
        cfg.fade_completed = False
    if parsed.language:
        from typr.storage.config import VALID_CODE_LANGUAGES
        lang_lower = parsed.language.lower()
        if lang_lower in VALID_CODE_LANGUAGES:
            cfg.mode = "code"
            cfg.code_language = lang_lower
        else:
            cfg.language = parsed.language

    # Launch interactive curses session
    app = TyprApp(cfg)
    try:
        app.launch()
    except KeyboardInterrupt:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())

