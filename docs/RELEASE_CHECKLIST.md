# TYPR — Open-Source Release Checklist (v0.1.0)

**Target Release:** v0.1.0  
**Current Status:** READY FOR RELEASE  
**Quality Standard:** Every check backed by concrete verification evidence.

---

## 1. Code Provenance & Legal Compliance

- [x] Initial codebase audit performed (`docs/PROJECT_AUDIT.md`).
- [x] Direct Monkeytype GPL code dependencies identified and replaced with clean-room implementations.
- [x] Proprietary/copied configuration structures removed and replaced with Typr native schema.
- [x] Wordlists verified for public domain / permissive open-source licensing.
- [x] Code snippets for programming mode verified for educational copyright compliance.
- [x] Final license selected (MIT License) and confirmed with user.
- [x] `LICENSE` file created (MIT License).
- [x] `THIRD_PARTY_NOTICES` created with proper attributions.

---

## 2. Architecture & Code Quality

- [x] Core typing engine decoupled from terminal/curses rendering (`src/typr/core/`).
- [x] Global mutable state eliminated; engine and sessions encapsulated in classes.
- [x] Type annotations applied to public interfaces, functions, and data models.
- [x] Robust error handling implemented for file I/O, database paths, and configuration parsing.
- [x] Clean modular package structure under `src/typr/`.
- [x] No unhandled exceptions on unexpected input or rapid keystrokes.

---

## 3. Terminal Reliability & Compatibility

- [x] Safe curses initialization and cleanup wrapped in guaranteed `safe_curses_run()`.
- [x] Terminal restored cleanly on `Ctrl+C` (SIGINT) without leaving cursor invisible or echo disabled.
- [x] Dynamic terminal window resize (`KEY_RESIZE`) handled gracefully without crashes.
- [x] Small terminal dimensions (< 40 columns or < 12 rows) handled with informative warning.
- [x] 256-color fallback and monochrome profiles (`mono`) verified for all terminal environments.
- [x] Hardware cursor state restored on exit via ANSI escape sequences (`\x1b[0 q`).

---

## 4. Feature Completeness

- [x] **Words Mode:** Configurable word counts (10, 25, 50, 100), punctuation, numbers.
- [x] **Time Mode:** Configurable durations (15s, 30s, 60s, 120s, custom) with continuous word buffer feeding.
- [x] **Quotes Mode:** Curated, verified quotes with author attribution.
- [x] **Programming Mode:** Syntax snippets for Python, Rust, C++, JavaScript, Go, Bash, SQL.
- [x] **Results Screen:** Net WPM, Raw WPM, Accuracy, Consistency, character statistics.
- [x] **Visual Performance Chart:** ASCII/Unicode WPM progress graph.
- [x] **History & Analytics:** Local SQLite storage, personal bests, historical averages, recent sessions table.
- [x] **CLI Capabilities:** `-t/--time`, `-w/--words`, `-m/--mode`, `-p`, `-n`, `-l`, `--stats`, `--history`, `--config-path`, `--reset-config`, `--clear-history`.

---

## 5. Verification & Testing

- [x] Unit tests for session engine state machine (`tests/test_core.py`).
- [x] Unit tests for WPM, Raw WPM, accuracy, and consistency math (`tests/test_core.py`).
- [x] Tests for backspace, word deletion, and character replacement (`tests/test_core.py`).
- [x] Tests for configuration loading, validation, and serialization (`tests/test_storage.py`).
- [x] Tests for SQLite history storage, aggregation, and querying (`tests/test_storage.py`).
- [x] Tests for all typing modes (`tests/test_modes.py`).
- [x] Tests for layout calculations and theme mapping (`tests/test_ui.py`).
- [x] Automated CLI invocation tests (`tests/test_cli.py`).
- [x] Full test suite execution: **41/41 tests passing in 0.012s**.

---

## 6. Packaging & Installation

- [x] `pyproject.toml` created with modern packaging standards (PEP 517/621).
- [x] `setup.py` shim created for backward compatibility.
- [x] CLI entry point `typr` configured (`typr = "typr.cli:main"`).
- [x] Package data (wordlists, snippets) correctly bundled in package configuration.
- [x] Direct `./typr` root launcher verified and operational.

---

## 7. Documentation & Community Health

- [x] `README.md` with product positioning, terminal diagrams, installation, and usage.
- [x] `CONTRIBUTING.md` with development setup and testing guidelines.
- [x] `CODE_OF_CONDUCT.md` created.
- [x] `SECURITY.md` with vulnerability reporting instructions.
- [x] `CHANGELOG.md` with v0.1.0 release notes.
- [x] `.github/ISSUE_TEMPLATE/` templates for bug reports and feature requests.
- [x] `.github/workflows/ci.yml` multi-Python CI workflow.
