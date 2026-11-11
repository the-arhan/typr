"""Performance benchmark suite for Typr.

Measures actual startup latency, input processing latency, memory usage,
and rendering layout calculation speed.
"""

from __future__ import annotations

import os
import resource
import time
from typing import List

from typr.core.engine import TypingEngine
from typr.core.session import SessionConfig
from typr.core.text_source import TextSource
from typr.storage.config import AppConfig, load_config
from typr.ui.layout import compute_line_layout


def benchmark_startup() -> float:
    """Measure configuration and engine initialization time in milliseconds."""
    t0 = time.perf_counter()
    cfg = load_config()
    source = TextSource(seed=123)
    words = source.generate_words(cfg.words)
    engine = TypingEngine(SessionConfig(mode="words", amount=cfg.words), words)
    t1 = time.perf_counter()
    return (t1 - t0) * 1000.0


def benchmark_keystroke_latency(num_keystrokes: int = 1000) -> float:
    """Measure average keystroke processing latency in microseconds."""
    words = ["benchmark", "typing", "performance", "terminal", "system"] * 50
    cfg = SessionConfig(mode="words", amount=len(words))
    engine = TypingEngine(cfg, words)

    t0 = time.perf_counter()
    for word in words[:num_keystrokes]:
        for ch in word:
            engine.press_key(ch)
        engine.press_space()
    t1 = time.perf_counter()

    total_keys = engine.total_keystrokes
    total_us = (t1 - t0) * 1_000_000.0
    return total_us / max(1, total_keys)


def benchmark_layout_speed(iterations: int = 500) -> float:
    """Measure time taken to compute wrapped layout lines for 100 words in microseconds."""
    words = ["extremely", "fast", "terminal", "native", "responsive", "layout"] * 20
    typed = [""] * len(words)

    t0 = time.perf_counter()
    for _ in range(iterations):
        compute_line_layout(words, typed, max_line_width=80)
    t1 = time.perf_counter()

    return ((t1 - t0) * 1_000_000.0) / iterations


def get_memory_rss_mb() -> float:
    """Return resident memory usage in megabytes."""
    usage = resource.getrusage(resource.RUSAGE_SELF)
    # ru_maxrss is in kilobytes on Linux
    return usage.ru_maxrss / 1024.0


def run_all_benchmarks() -> None:
    print("\n  ========================================")
    print("         TYPR PERFORMANCE BENCHMARK")
    print("  ========================================")

    # 1. Startup
    startup_runs = [benchmark_startup() for _ in range(10)]
    avg_startup = sum(startup_runs) / len(startup_runs)
    print(f"  Startup Latency:           {avg_startup:.3f} ms (p95: {max(startup_runs):.3f} ms)")

    # 2. Keystroke Latency
    key_lat = benchmark_keystroke_latency(200)
    print(f"  Input Processing Latency:  {key_lat:.3f} μs / key")

    # 3. Layout Rendering
    layout_lat = benchmark_layout_speed(500)
    print(f"  Layout Calculation Time:   {layout_lat:.3f} μs / frame")

    # 4. Memory Footprint
    mem = get_memory_rss_mb()
    print(f"  Memory Footprint (RSS):    {mem:.2f} MB")
    print("  ========================================\n")


if __name__ == "__main__":
    run_all_benchmarks()

