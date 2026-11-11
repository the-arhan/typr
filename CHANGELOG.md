# Changelog

All notable changes to **Typr** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.25] - 2026-11-11

### Phase 1.25: Visual Identity, Focus Mode & Typing Experience Refinement

#### Added
- **Distraction-Free Focus Mode:**
  - Fast toggle via `Ctrl+F` during any active session or via `--focus` command line flag.
  - Strips all chrome, telemetry, and navigation to present a clean, centered typing canvas.
  - Seamless exit via `Ctrl+F` or `Esc` without resetting test metrics.
- **Larger, Readable Typography:**
  - Adaptive 3-row line spacing on viewports with height $\ge 24$, giving a 1.5x vertical presence increase.
  - Configurable `text_size` (`large`, `normal`, `adaptive`) with spacious inter-word spacing in prose modes while strictly preserving authentic indentation in programming mode.
- **Completed-Word Fading:**
  - Successfully typed words fade to subtle dimmed text (`fade_completed: bool`), enhancing visual focus on upcoming and active words.
  - Past uncorrected typos preserve red underlines so mistakes remain identifiable.
- **Smooth Caret Following:**
  - Visually decoupled smooth caret interpolation toward the logical cursor position without introducing input lag.
  - Automatic line break snapping to prevent diagonal jumps across rows.
- **Menu & CLI Extensions:**
  - Menu toggles for Focus mode (`f`), text size (`s`), smooth caret (`c`), and completed word fading (`w`).
  - Added CLI flags: `--focus`, `--text-size`, `--no-smooth-caret`, `--no-fade`.
  - Added programming snippets for HTML and CSS.

---

## [0.1.0] - 2026-11-10

### Initial Public Release

#### Added
- **Core Engine:**
  - Fully decoupled, zero-curses typing engine with deterministic state transitions (`IDLE`, `READY`, `RUNNING`, `COMPLETED`, `ABORTED`).
  - Standardized typing metrics: Net WPM, Raw WPM, attempt-based Accuracy, and statistical Consistency (via Coefficient of Variation).
  - High-precision monotonic session timer with pause and resume support.
- **Typing Modes:**
  - **Words Mode:** Configurable word counts (10, 25, 50, 100), with punctuation and number generation.
  - **Time Mode:** Configurable durations (15s, 30s, 60s, 120s) with seamless word buffer extension.
  - **Quotes Mode:** Curated literature and technical quotations with author attribution.
  - **Programming Mode:** Practice material for Python, Rust, C++, JavaScript, Go, Bash, and SQL with syntax-authentic indentation and symbols.
- **Terminal UI & Visual Identity:**
  - Three distinct palettes: Graphite + Electric Mint (`mint`), Obsidian + Warm Amber (`amber`), and Deep Navy + Restrained Cyan (`cyan`).
  - High-contrast monochrome accessibility profile (`mono`) utilizing text intensity, underlining, and dim attributes.
  - Smooth multi-line line-wrapping canvas with active line centering.
  - Detailed post-test analysis screen with 2x4 metrics grid and an ASCII/Unicode speed-over-time bar graph.
  - Clean keyboard-driven quick settings menu (`Esc`).
- **Storage & Local Analytics:**
  - Clean, strongly-typed JSON configuration in `$XDG_CONFIG_HOME/typr/config.json`.
  - Local-first, zero-telemetry SQLite session logging in `$XDG_DATA_HOME/typr/history.db`.
  - Tracking for personal bests, historical averages, total time typed, and recent sessions.
- **CLI Capabilities:**
  - One-off mode and duration overrides: `-t/--time`, `-w/--words`, `-m/--mode`, `-p/--punctuation`, `-n/--numbers`, `-l/--language`.
  - Offline inspection flags: `--stats`, `--history`, `--config-path`, `--reset-config`, `--clear-history`.
- **Packaging & Reliability:**
  - PEP 517/621 `pyproject.toml` configuration with executable entry point `typr`.
  - Full suite of 41 unit and integration tests passing in under 20ms.
  - Guaranteed terminal restoration on unexpected termination, resize, or `Ctrl+C`.

