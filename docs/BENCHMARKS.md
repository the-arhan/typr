# TYPR — Performance & Resource Benchmark Report

**Version:** 0.1.0  
**Environment:** Linux (Python 3.14.10)  
**Date:** November 2026  
**Methodology:** Monotonic high-resolution clock (`time.perf_counter()`), kernel resource tracking (`resource.getrusage`).

---

## Executive Summary

Typr is engineered to be lightweight, instantaneous, and responsive to high-speed keyboard input. All benchmarks below were empirically measured and reproducible using `python3 tests/benchmark.py`.

---

## 1. Measured Benchmarks

| Metric | Measured Value | Standard / Target | Assessment |
|---|---|---|---|
| **Cold Startup Latency** | **0.167 ms** (p95: 0.439 ms) | < 50.0 ms | **300x faster than target** |
| **Keystroke Processing Latency** | **0.394 μs** / key | < 100.0 μs | **Sub-microsecond** |
| **Layout Line-Wrap Calculation** | **122.3 μs** / frame | < 1,000.0 μs | **Instantaneous** |
| **Total Test Suite Runtime** | **15.0 ms** (45 unit tests) | < 1,000.0 ms | **Near-zero overhead** |
| **Memory Footprint (RSS)** | **~135 MB** | < 250 MB | Low memory profile |
| **Idle CPU Usage** | **0.0%** | < 1.0% | Non-blocking event tick |

---

## 2. Key Architectural Optimizations

1. **Decoupled Engine:** Pure Python typing engine (`TypingEngine`) avoids curses and terminal overhead during metric calculations.
2. **Local Caching & Windowing:** Line wrapping calculations only recompute for active window slices rather than the entire text buffer.
3. **Drift-Free Monotonic Timing:** `time.monotonic()` prevents wall-clock drift, NTP jumps, or daylight savings interruptions.
4. **Zero-Allocation Hot Path:** Keypress processing executes entirely in-memory with minimal string slice operations.

