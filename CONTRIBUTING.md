# Contributing to Typr

Thank you for your interest in contributing to **Typr**! We welcome contributions from developers, designers, and terminal enthusiasts.

## Philosophy & Guiding Principles

- **Terminal-Native:** Typr is designed specifically for terminal emulators. We prioritize speed, low latency, and distraction-free usability over visual clutter.
- **Offline-First:** Typr will never require an internet connection, accounts, or telemetry.
- **Clean Architecture:** Core typing engine and metrics calculations have zero dependencies on `curses` and must remain independently unit-testable.

---

## Development Setup

### 1. Prerequisites
- Python 3.8 or higher.
- A terminal emulator supporting ANSI color codes and standard cursor shapes.

### 2. Clone and Setup
```bash
git clone https://github.com/the-arhan/typr.git
cd typr
```

Run Typr directly in development mode:
```bash
./typr
```

Or run via module syntax:
```bash
PYTHONPATH=src python3 -m typr
```

---

## Running Automated Tests

Typr includes a comprehensive unit and integration test suite:

```bash
PYTHONPATH=src python3 -m unittest discover tests
```

To run individual test modules:
```bash
PYTHONPATH=src python3 -m unittest tests/test_core.py
PYTHONPATH=src python3 -m unittest tests/test_storage.py
PYTHONPATH=src python3 -m unittest tests/test_modes.py
PYTHONPATH=src python3 -m unittest tests/test_ui.py
PYTHONPATH=src python3 -m unittest tests/test_cli.py
```

All pull requests must pass all tests before being merged.

---

## Project Structure

```
src/typr/
├── __init__.py           # Package version and metadata
├── __main__.py           # python -m typr entry point
├── cli.py                # Command-line argument parsing and inspection flags
├── app.py                # Application coordinator & event loop
├── core/                 # Decoupled core engine (zero curses dependency)
│   ├── engine.py         # Typing engine state machine and input evaluator
│   ├── metrics.py        # Standard WPM, accuracy, and consistency math
│   ├── session.py        # Session state models and results
│   ├── timer.py          # Monotonic drift-free timer
│   └── text_source.py    # Word generation and snippet loaders
├── modes/                # Mode implementations (Words, Time, Quotes, Code)
├── storage/              # Configuration & SQLite local history
├── ui/                   # Terminal layout, curses screens, themes, widgets
└── data/                 # Wordlists and code snippets
```

---

## Code Style & Conventions

- Use type hints on all function signatures and public dataclasses.
- Ensure all screen rendering calls handle bounds gracefully (`safe_addstr`).
- Do not add external runtime dependencies unless justified and discussed.
- Ensure terminal restoration is guaranteed in all code paths.

---

## Submitting Pull Requests

1. Fork the repository and create a feature branch (`git checkout -b feature/my-enhancement`).
2. Implement your changes with accompanying tests in `tests/`.
3. Verify that all unit tests pass cleanly.
4. Commit with descriptive commit messages.
5. Open a Pull Request on GitHub.

