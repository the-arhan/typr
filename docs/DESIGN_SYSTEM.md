# TYPR — Product Identity & Terminal Design System

**Version:** 1.0.0  
**Status:** Approved  
**Brand Philosophy:** *"Type better. Stay in flow."*

---

## 1. Product Positioning & Identity

Typr is a terminal-native typing trainer designed for developers, system administrators, and keyboard-centric users who live inside terminal emulators.

Unlike browser-based trainers wrapped in web frames, Typr:
- Starts in milliseconds with zero loading latency.
- Remains 100% keyboard-driven without requiring a mouse.
- Consumes minimal RAM and zero idle CPU cycles.
- Operates completely offline with zero telemetry or tracking.
- Embraces terminal-native typography, ASCII/Unicode geometry, and adaptive layout.

---

## 2. Visual Identity & Themes

Typr adopts an understated, calm, technical aesthetic that keeps the focus squarely on the typing target. Three distinct color directions are built-in, complemented by a high-contrast monochrome accessibility profile.

### 2.1 Default Theme: Graphite + Electric Mint (`mint`)
An ultra-clean dark graphite background accented with energetic mint green.
- **Background:** `#18191c` (Deep graphite)
- **Surface / Panel:** `#222428`
- **Text Primary:** `#e2e4e9` (Crisp off-white)
- **Text Untyped / Muted:** `#525866` (Subtle slate gray)
- **Correct Character:** `#e2e4e9` (Promoted to bright clear white)
- **Incorrect Character:** `#ff5c5c` (Punchy red error)
- **Incorrect Extra Character:** `#d63333` (Underlined crimson)
- **Accent / Electric Mint:** `#00f59b` (Vibrant electric mint)
- **Cursor Indicator:** `#00f59b` (Matching mint cursor)
- **Warning / Sub:** `#e5c07b` (Warm gold)

### 2.2 Warm Theme: Obsidian + Warm Amber (`amber`)
Inspired by vintage amber CRT terminals and warm mechanical setups.
- **Background:** `#121214` (Obsidian black)
- **Surface:** `#1e1e24`
- **Text Primary:** `#f3ede2`
- **Text Untyped:** `#5c564c`
- **Correct Character:** `#f3ede2`
- **Incorrect Character:** `#ff4d4d`
- **Accent / Amber:** `#f5a623` (Radiant warm amber)
- **Cursor Indicator:** `#ffb84d`

### 2.3 Oceanic Theme: Deep Navy + Restrained Cyan (`cyan`)
A cool, technical, night-shift palette.
- **Background:** `#0d1117` (Deep navy)
- **Surface:** `#161b22`
- **Text Primary:** `#c9d1d9`
- **Text Untyped:** `#484f58`
- **Correct Character:** `#c9d1d9`
- **Incorrect Character:** `#ff7b72`
- **Accent / Cyan:** `#58a6ff` (Restrained technical cyan)
- **Cursor Indicator:** `#79c0ff`

### 2.4 Accessibility: High-Contrast Monochrome (`mono`)
For terminals without color support or users requiring maximum contrast.
- Uses standard terminal foreground and background.
- Employs **Bold**, **Underline**, and **Dim** attributes instead of hue.
- Untyped characters are rendered **DIM**.
- Correct characters are rendered **NORMAL**.
- Incorrect characters are rendered **UNDERLINE + REVERSE / BOLD**.
- Cursor is marked with hardware underline / block or bracket framing.

---

## 3. Typography & Terminal Layout Guidelines

### 3.1 Terminal Dimensions & Scaling
- **Minimum Supported Dimensions:** 40 columns × 12 rows.
- **Ideal Viewport:** 80–100 columns × 24 rows.
- **Maximum Text Line Width:** Responsive, clamped between 30 and 80 columns to maintain comfortable visual scanning distance (averaging 8–12 words per line).

### 3.2 Spatial Composition
```
┌────────────────────────────────────────────────────────┐
│ typr  •  words 25  •  english                esc: menu │ Top Bar
│                                                        │
│                                                        │
│   24 wpm   98% acc   0:14                              │ Live Telemetry
│                                                        │
│   The quick brown fox jumps over the lazy dog.         │ Target Text
│   Pack my box with five dozen liquor jugs.             │ (Active Word Focused)
│   How vexingly quick daft zebras jump!                 │
│                                                        │
│                                                        │
│ [tab] restart   [esc] menu   [ctrl+w] del-word         │ Bottom Bar
└────────────────────────────────────────────────────────┘
```

### 3.3 Visual Hierarchy Principles
1. **The Typing Canvas is Sacred:** The typing text is centered vertically and horizontally. Distractions, flashing borders, and unnecessary ASCII art are strictly prohibited.
2. **Non-Color Affirmation:** Incorrect characters are highlighted with both color and underline styling so that color deficiency does not prevent error detection.
3. **Smooth Scroll & Multi-Line Windowing:** In multi-line texts (quotes, code snippets, or lengthy word sessions), the viewport smoothly displays the previous line, the active line, and upcoming lines.

