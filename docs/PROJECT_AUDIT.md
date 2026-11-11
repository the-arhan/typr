# TYPR — Comprehensive Project Audit & Technical Baseline

**Document Version:** 1.0.0  
**Date:** November 2026  
**Auditor:** Typr Senior Product & Architecture Team  
**Scope:** Initial Discovery, Code Provenance, Technical Debt, and Architecture Migration Plan

---

## 1. Executive Summary

`Typr` is currently a single-file, 932-line Python script (`typr`) providing an interactive terminal typing experience using Python's standard `curses` library. 

While the prototype functions as a runnable script, it is tightly coupled to Monkeytype's web application configuration, algorithms, and styling conventions. It possesses zero automated tests, relies on global mutable state, lacks modular packaging (`pyproject.toml`), and has no programming mode, quote mode, or persistent historical analytics beyond high-score caching.

This audit establishes the baseline of the current code, conducts a thorough provenance and licensing assessment, documents technical debt and portability hazards, identifies capabilities to preserve, and provides an actionable blueprint for evolving Typr into a distinctive, production-grade, open-source terminal application.

---

## 2. Baseline Architecture & Operational Flow

### 2.1 File & Directory Structure
The repository contains only two tracked entities:
- `.git/`: A freshly initialized Git repository with no prior commits on `main`.
- `typr`: A 932-line executable Python 3 script with `+x` permissions (`chmod 755`).

No package manifests (`pyproject.toml`, `setup.cfg`), no test suites (`tests/`), and no documentation files existed prior to this audit.

### 2.2 Application Lifecycle & Control Flow

```
[CLI Invocation: ./typr]
          │
          ▼
    main() entry point
    ├── Sets locale & checks UTF-8 capability (UNICODE)
    ├── Parses arguments (-t, -w, -p, -n, --import-config, --config-path)
    ├── Loads ~/.config/typr/config.json (or defaults from DEFAULT_CONFIG string)
    └── curses.wrapper(run, dirty)
          │
          ▼
    run(scr, dirty)
    ├── Initializes colors via init_colors(scr) & 256-color palette approximation
    ├── Configures curses (keypad=True, timeout=50ms)
    ├── Sets hardware cursor style via terminal escape sequences (\x1b[5 q)
    ├── Loads personal bests from ~/.local/share/typr/pbs.json
    ├── Initializes Test(current_cfg())
    └── Event Loop (50ms tick rate)
          ├── Recolor dynamic themes (e.g. RGB rainbow cycling)
          ├── Update cursor visibility
          ├── Render Active Screen:
          │     ├── "test"    -> draw_test()
          │     ├── "results" -> draw_results()
          │     └── "menu"    -> draw_menu()
          ├── Non-blocking Key Acquisition: scr.get_wch()
          └── Process Input:
                ├── Screen = "test":
                │     ├── Escape     -> Switch to "menu"
                │     ├── QuickRestart (Tab/Enter) -> New Test
                │     ├── Backspace  -> test.backspace()
                │     ├── Ctrl+W     -> test.delete_word()
                │     └── Printable  -> test.press(char)
                └── Screen = "results" / "menu":
                      ├── Enter / Tab / Esc -> Restart / Back
                      ├── 'q' -> Exit run()
                      └── Menu keys (1-8, p, n, d) -> Update settings
          │
          ▼
    Shutdown & Terminal Cleanup
    ├── curses.wrapper() restores canonical terminal mode and normal cursor
    ├── reset_caret_style() issues \x1b[0 q to restore terminal default cursor
    └── Saves modified settings to config.json if dirty
```

### 2.3 Detailed Mechanism Analysis

| Component | Current Implementation | Observations & Weaknesses |
|---|---|---|
| **Entry Point** | Monolithic `main()` in root `typr` script | Cannot be installed as a standard Python package; relies on relative directory execution or manual symlinking. |
| **Settings Management** | Global dictionary `S`, loaded from JSON | 65+ configuration keys directly copied from Monkeytype web app export. Most keys (e.g., `ads`, `monkeyPowerLevel`, `funbox`, `accountChart`) are dead code. |
| **Word Generation** | `WordSource` using static list of 105 English words | Very small vocabulary; repetitive. Punctuation and numbers are generated probabilistically using hardcoded arbitrary thresholds. |
| **Typing Engine** | `Test` class in `typr` | Manages input buffers, accuracy counters, and per-second snapshots. Tightly bound to curses screen dimensions and global settings `S`. |
| **Metrics Calculation** | Net WPM: `correct_chars / 5 / mins`<br>Raw WPM: `typed_chars / 5 / mins`<br>Accuracy: `keys_ok / keys_total * 100` | Metric math is standard, but accuracy is attempt-based rather than final-text based. Consistency uses Monkeytype's tanh coefficient-of-variation formula. |
| **Rendering** | Direct `scr.addstr()` with manual coordinate math | Uses fixed line height spacing (`top + r * 2`). Hardcoded breakpoints (`rows < 10 or cols < 36`). Assumes 1 monospace column per Unicode code point. |
| **Palette / Color** | `nearest256()` Euclidean distance mapping in RGB 6x6x6 cube | Useful fallback for 256-color terminals, but does not leverage truecolor (direct 24-bit RGB) where available in modern terminals. |
| **History / Persistence** | High-score map in `pbs.json` | Stores only highest WPM per mode key (e.g., `time15p`). No historical session logs, no speed graphs over days/weeks, no error heatmaps. |

---

## 3. Code Provenance and Licensing Assessment

### 3.1 Provenance Findings
1. **Monkeytype Relationship:**
   - Monkeytype is an open-source typing application created by MiKi and contributors, licensed under the **GNU General Public License v3.0 (GPL-3.0)**.
   - The existing `typr` script includes:
     - Direct declaration in docstring: *"a Monkeytype-style typing test for your terminal, driven by a Monkeytype config file."*
     - Exact duplicate of Monkeytype's JSON export structure in `DEFAULT_CONFIG`.
     - Exact theme schema ordering `("bg", "main", "caret", "sub", "subAlt", "text", "error", "errorExtra", "colorfulError", "colorfulErrorExtra")`.
     - Direct inclusion of the Monkeytype theme `"serika_dark"`.
     - Re-implementation of Monkeytype's consistency algorithm polynomial: `cov + cov**3 / 3 + cov**5 / 5` inside `math.tanh()`.
     - Mimicked difficulty mechanics (`expert` = fail on wrong word submit; `master` = fail on wrong character).

### 3.2 Licensing Implications
- **GPL-3.0 Copyleft Risk:** Because components of the existing code and configuration schema were copied or adapted from Monkeytype, redistributing Typr under a permissive license (such as MIT or Apache-2.0) without remediation would constitute copyright infringement if Monkeytype's GPL-3.0 terms apply to those elements.
- **Remediation Strategy for Independence:**
  1. **Clean Configuration Schema:** Retire the 65-key Monkeytype JSON configuration schema. Replace it with a clean, native, documented Typr configuration (in standard TOML/JSON format) containing only settings Typr actually implements.
  2. **Independent Theme System:** Design an original Typr color system (Graphite + Electric Mint, Obsidian + Warm Amber, Deep Navy + Restrained Cyan) with semantic tokens (`bg`, `surface`, `text_primary`, `text_muted`, `correct`, `error`, `cursor`, `accent`). Remove copied theme definitions.
  3. **Original Metric Calculations:** Standardize WPM and accuracy on published typing competition standards (standard 5-character word convention, explicitly separating net WPM, raw WPM, gross typing accuracy, and completion accuracy). Replace the polynomial consistency formula with a standard, documented statistical metric (Coefficient of Variation or Pearson standard error percentage).
  4. **Original Content:** Replace the 105-word list with curated, open-source licensed wordlists (e.g. from public domain word frequency databases) and authentic programming language snippet datasets.
  5. **Licensing Determination:** Once clean-room independence is established, Typr can safely adopt a clean open-source license (such as **MIT** or **GPL-3.0**, pending final user approval).

---

## 4. Technical Debt & Portability Risks

### 4.1 Identified Technical Debt
1. **Monolithic Architecture:** All components (CLI, configuration, session engine, metrics, curses drawing, ANSI escape formatting, disk persistence) reside in a single file without modular isolation.
2. **Global Mutable State:** The `S` dictionary is modified across multiple functions. State leaks across tests and makes concurrent testing impossible.
3. **Lack of Automated Verification:** Not a single unit test exists. Refactoring cannot be verified without manual execution.
4. **Fragile Input Handling:** Characters are read via `scr.get_wch()`, but multi-byte sequences, paste events, or unusual key combinations can cause uncaught exceptions or unresponsive states.
5. **Unicode & CJK Display Defects:** Coordinate calculation assumes `len(word)` equals terminal column width. For wide Unicode characters or combining accents, cursor drift and visual corruption occur.
6. **No Code / Programming Mode:** The user requested programming mode (Python, Rust, C++, JS/TS, Go, Bash, SQL) with bracket/symbol handling, which is completely missing.
7. **No Session History:** No detailed session history or analytical trends are saved.

### 4.2 Portability & Compatibility Risks
1. **Windows Support:** Standard Python `curses` is not available on Windows out of the box (requires `windows-curses`). Architecture must isolate curses and support safe degradation or platform-specific dependencies.
2. **Terminal Dimensions:** If the terminal is resized below 36 columns or 10 rows, rendering breaks or displays an unstyled error string without recovery logic.
3. **Hardware Cursor Sequences:** Direct ANSI escape writes to `os.write(1, ...)` (`\x1b[5 q`) assume VT100/Xterm cursor control support. In terminals without DEC private mode 50 cursor shapes, escape sequences may either be ignored or rendered as visible garbage.

---

## 5. Capabilities to Preserve

The following core behaviors are effective and must be preserved during modernization:
1. **Immediate Startup & Keyboard Responsiveness:** Zero noticeable startup delay; immediate key readiness.
2. **Keyboard-Driven Workflow:** Seamless restart via Tab/Enter; quick word deletion via Ctrl+W; menu access via Esc.
3. **Live Typing Visual Feedback:** Real-time character highlighting (correct vs. error vs. untyped), subtle cursor tracking, live WPM and accuracy indicators.
4. **Speed Over Time Graph:** Visual sparkline/bar graph on results screen plotting WPM progression across test duration.
5. **Configurable Word & Time Modes:** Flexible durations (15s, 30s, 60s, 120s) and word counts (10, 25, 50, 100), with punctuation and number toggles.
6. **Zero Cloud Requirement:** Completely offline, no network calls, no analytics beacons, absolute privacy.

---

## 6. Target Architecture & Modular Design

```
src/typr/
├── __init__.py                 # Package version & top-level exports
├── __main__.py                 # python -m typr entry point
├── cli.py                      # Clean argparse / CLI command router
├── app.py                      # Application coordinator & event loop
├── core/                       # Independent Core Engine (curses-free)
│   ├── __init__.py
│   ├── engine.py               # Typing engine & state transitions
│   ├── session.py              # Session lifecycle (IDLE, READY, RUNNING, COMPLETED)
│   ├── metrics.py              # Deterministic WPM, Raw WPM, Accuracy, Consistency
│   ├── timer.py                # Monotonic session timer with pause/elapsed tracking
│   └── text_source.py          # Word generator, quote provider, code snippet provider
├── ui/                         # Terminal Presentation & Curses
│   ├── __init__.py
│   ├── terminal.py             # Curses terminal lifecycle, safe init & restoration
│   ├── layout.py               # Responsive column & line wrapping calculations
│   ├── renderer.py             # Screen renderer & character state painter
│   ├── screens.py              # Test screen, Results screen, Menu/Settings screen
│   ├── themes.py               # Independent color palette definitions & 256/truecolor mapping
│   └── widgets.py              # WPM graph, live stats bar, key hints
├── modes/                      # Typing Modes
│   ├── __init__.py
│   ├── base.py                 # Mode contract & interface
│   ├── words.py                # Words mode (10, 25, 50, 100)
│   ├── time.py                 # Time mode (15s, 30s, 60s, 120s)
│   ├── quotes.py               # Quote mode with verified licensed quotes
│   └── code.py                 # Programming language code snippets (Python, Rust, etc.)
├── storage/                    # Persistence Layer
│   ├── __init__.py
│   ├── paths.py                # XDG-compliant path resolution
│   ├── config.py               # Clean, validated configuration schema & IO
│   └── history.py              # SQLite / JSON session history & local analytics
└── data/                       # Static Data Assets
    ├── wordlists/              # Curated open-source wordlists
    └── snippets/               # Syntax-valid code snippets for programming mode
```

---

## 7. Proposed Phased Implementation Sequence

1. **Phase 0 (Current):** Discovery, baseline documentation, audit deliverable, safety tracking documents.
2. **Phase 1:** Product Identity & Design System (original visual language: Graphite + Electric Mint, clean typography, theme engine).
3. **Phase 2:** Package Restructuring & Core Architecture (`src/typr/` layout, decoupling core from curses).
4. **Phase 3:** Terminal UI & Robust Curses Engine (clean rendering, resize handling, flicker-free updates, hardware cursor safety).
5. **Phase 4:** Typing Engine & Deterministic Metrics (lifecycle state machine, independent testable unit tests).
6. **Phase 5:** Typing Modes (Words, Time, Quotes, and Programming Code mode with realistic multi-language snippets).
7. **Phase 6:** Clean Configuration System (TOML/JSON format, schema validation, reset commands).
8. **Phase 7:** Local Storage & Analytics (XDG paths, structured SQLite session history, personal bests, trends).
9. **Phase 8:** Modern CLI Interface (`typr`, `typr --duration`, `typr --mode`, `typr --stats`, `typr --history`, etc.).
10. **Phase 9:** Terminal Compatibility & Signal Handling (clean exit on Ctrl+C, window resize, terminal restoration).
11. **Phase 10:** Usability & Accessibility (colorblind/high-contrast modes, fallback for limited terminals).
12. **Phase 11:** Performance Benchmarks & Zero-Flicker Verification (low memory footprint, <100ms startup).
13. **Phase 12:** Automated Testing Suite (`tests/` covering unit, integration, CLI, and metrics).
14. **Phase 13:** Python Packaging (`pyproject.toml`, standard build hooks, wheel/sdist generation).
15. **Phase 14:** Open Source Documentation (README, CONTRIBUTING, LICENSE, CODE_OF_CONDUCT, SECURITY, THIRD_PARTY_NOTICES).
16. **Phase 15:** Release Management (v0.1.0 checklist, verification).
17. **Phase 16:** Final Quality Review.

---

## 8. Verification & Next Steps
- Baseline audit complete.
- Implementation status document created at `docs/IMPLEMENTATION_STATUS.md`.
- Release checklist created at `docs/RELEASE_CHECKLIST.md`.
- Original `typr` script preserved untouched. Ready to proceed to Phase 1 upon confirmation.

