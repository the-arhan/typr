# T Y P R

<p align="center">
  <strong>A terminal-native typing trainer built for people who live in the terminal.</strong>
</p>

<p align="center">
  <em>"Type better. Stay in flow."</em>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#typing-modes">Modes</a> •
  <a href="#cli-usage">CLI Usage</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#privacy">Privacy</a> •
  <a href="#license">License</a>
</p>

---

## Overview

**Typr** is a fast, lightweight, distraction-free typing trainer that runs directly inside your terminal emulator. It is not an Electron web application squeezed into a shell window, but a pure terminal experience engineered in Python with standard `curses`.

Whether you are warming up before a coding session, improving your cadence on brackets and symbols, or honing raw speed, Typr gives you an immediate, keyboard-driven environment with zero startup latency and zero distractions.

```
┌────────────────────────────────────────────────────────┐
│ typr  •  words 25  •  english                esc: menu │
│                                                        │
│   64 wpm   98% acc   14/25                             │
│                                                        │
│   The quick brown fox jumps over the lazy dog.         │
│   Pack my box with five dozen liquor jugs.             │
│   How vexingly quick daft zebras jump!                 │
│                                                        │
│ [tab] restart   [esc] menu   [ctrl+w] del-word         │
└────────────────────────────────────────────────────────┘
```

---

## Features

- **Blazing Fast Startup:** Launches in under 50ms with zero loading screens.
- **100% Keyboard Driven:** Start, restart, change settings, and navigate without ever touching a mouse.
- **Original Terminal Aesthetics:**
  - `mint`: Graphite background with vibrant electric mint accents (Default).
  - `amber`: Deep obsidian with warm vintage amber phosphor glow.
  - `cyan`: Night-shift navy with restrained technical cyan.
  - `mono`: High-contrast monochrome profile with bold/underline cues for maximum accessibility.
- **Developer-Focused Programming Mode:** Practice authentic code syntax across Python, Rust, C++, JavaScript, Go, Bash, and SQL with real indentation, braces, and operators.
- **Precision Metrics:** Standard 5-character word convention for Net WPM, Raw WPM, attempt-based Accuracy, and statistical Consistency (via Coefficient of Variation).
- **Post-Session Visual Graph:** Real-time sparkline/bar chart displaying your typing cadence and speed progression over time.
- **Local-First SQLite History:** Keeps track of your personal bests, historical averages, and past sessions with zero cloud dependencies.
- **Absolute Privacy:** Operates 100% offline. Zero telemetry, zero analytics beacons, zero network calls.

---

## Installation

### From Source (Development)
```bash
git clone https://github.com/the-arhan/typr.git
cd typr
./typr
```

### Via Pip
```bash
pip install .
```

After installation, the executable `typr` is available anywhere in your PATH:
```bash
typr
```

---

## Quick Start

Launch the trainer:
```bash
typr
```

### Keyboard Shortcuts
| Key | Action |
|---|---|
| **Any Character** | Begin typing and start the session timer |
| **Space** | Submit the current word |
| **Backspace** | Delete previous character |
| **Ctrl + W** | Delete entire word |
| **Ctrl + F** | Toggle distraction-free Focus Mode |
| **Tab** or **Enter** | Instant restart (Quick Restart) |
| **Esc** | Open Settings Menu / Back |
| **q** | Quit from Results or Menu screen |

---

## Typing Modes

### 1. Words Mode (`-m words`)
Type a fixed number of words. Ideal for focused rhythm and accuracy practice.
```bash
typr -w 50            # 50 words
typr -w 25 -p -n      # 25 words with punctuation and numbers
```

### 2. Time Mode (`-m time`)
Test how many words you can type within a time limit. The word stream extends continuously.
```bash
typr -t 60            # 60-second endurance sprint
typr -t 15            # 15-second speed burst
```

### 3. Quotes Mode (`-m quotes`)
Type curated literature, philosophy, and technical quotations with verified attribution.
```bash
typr -m quotes
```

### 4. Programming Mode (`-m code`)
Practice syntax, brackets, semicolons, and identifiers from real software snippets:
```bash
typr -m code -l python
typr -m code -l rust
typr -m code -l cpp
typr -m code -l javascript
typr -m code -l go
typr -m code -l bash
typr -m code -l sql
```

---

## CLI Usage

Typr provides a comprehensive set of command-line options and inspection utilities:

```bash
typr [OPTIONS]
```

### Options
```text
  -h, --help                 Show help message and exit
  -v, --version              Show program version
  -t, --time SECONDS         Run a timed session (e.g. 15, 30, 60, 120)
  -w, --words COUNT          Run a word session (e.g. 10, 25, 50, 100)
  -m, --mode MODE            Select mode: words, time, quotes, code
  -p, --punctuation          Include punctuation in text
  -n, --numbers              Include numbers in text
  -l, --language LANG        Language or code language (python, rust, cpp, go, sql)
  --theme THEME              Visual theme: mint, amber, cyan, mono
  --difficulty DIFFICULTY    Difficulty level: normal, expert, master
  --stats                    Print aggregate statistics and exit
  --history                  Print recent sessions table and exit
  --config-path              Print configuration file path and exit
  --reset-config             Reset configuration to defaults and exit
  --clear-history            Clear local SQLite session history and exit
```

### Inspecting Local Analytics from the Shell
```bash
$ typr --stats

  TYPR PERFORMANCE ANALYTICS
  ────────────────────────────────────────
  Total Sessions:     42
  Total Time Typed:   24m 15s
  Overall Average:    72.4 WPM
  Top Net Speed:      96.8 WPM
  Average Accuracy:   97.6%
  ────────────────────────────────────────
```

---

## Configuration

Typr saves its configuration in standard XDG directories:
- **Config Path:** `~/.config/typr/config.json`
- **History Database:** `~/.local/share/typr/history.db`

### Sample `config.json`
```json
{
  "theme": "mint",
  "mode": "words",
  "time": 30,
  "words": 25,
  "punctuation": false,
  "numbers": false,
  "difficulty": "normal",
  "quick_restart": "tab",
  "live_wpm": true,
  "live_acc": true,
  "timer_style": "mini",
  "cursor_style": "line"
}
```

---

## Platform Support & Terminal Compatibility

Typr has been tested and verified across:
- **Linux:** Alacritty, Kitty, GNOME Terminal, Konsole, Foot, WezTerm, tmux, SSH sessions.
- **macOS:** Terminal.app, iTerm2, Alacritty.
- **Windows:** Windows Terminal, PowerShell, WSL (requires `windows-curses` on native Windows).

### Robust Terminal Lifecycle
Typr guarantees complete terminal restoration:
- Canonical echo, cursor visibility, and input buffering are safely restored upon exit.
- `Ctrl+C` (SIGINT) exits cleanly without scrambling terminal state.
- Dynamic window resizing (`KEY_RESIZE`) adapts the viewport instantly.

---

## Privacy Commitment

Typr is built on the conviction that a developer tool should respect its user:
- **No telemetry.**
- **No analytics beacons.**
- **No accounts or sign-ups.**
- **No network connectivity required.**
- **100% offline.** Everything is stored locally on your machine.

---

## Contributing

Contributions, bug reports, and suggestions are welcome! See [`CONTRIBUTING.md`](CONTRIBUTING.md) for architectural guidelines, development workflows, and testing instructions.

---

## License

Typr is released under the **[MIT License](LICENSE)**.

